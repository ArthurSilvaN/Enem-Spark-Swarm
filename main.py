import os
import requests
import zipfile
import time
import logging
import glob
import subprocess
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, LongType, IntegerType, StringType, DoubleType
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnemPipeline")

# Anotar tempo total
start_total = time.time()

# Configuração geral
YEARS = [2020, 2021, 2023]
HDFS_URI = "hdfs://namenode:8020"
LOCAL_PARQUET_BASE = "/data/enem_clean"
LOCAL_RESULTS_BASE = "/data/enem_results"

# Função de download + unzip
def download_and_extract(year):
    url = f"https://download.inep.gov.br/microdados/microdados_enem_{year}.zip"
    local_zip = f"enem{year}.zip"
    extract_dir = f"/data/enem_data/{year}"

    if not os.path.exists(local_zip):
        os.makedirs(extract_dir, exist_ok=True)

    logger.info(f"Verificando arquivo {local_zip} para o ano {year}")
    
    csv_pattern = os.path.join(extract_dir, "DADOS", "MICRODADOS_ENEM_*.csv")
    csv_files = glob.glob(csv_pattern)
    local_csv_path = csv_files[0]
    if not os.path.exists(local_csv_path):
        if not os.path.exists(local_zip):
            logger.info(f"Baixando {year} de {url}")

            session = requests.Session()
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            session.mount("https://", HTTPAdapter(max_retries=retries))

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            try:
                with session.get(url, stream=True, headers=headers, timeout=60) as r:
                    r.raise_for_status()
                    with open(local_zip, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao baixar {url}: {e}")
                raise
        else:
            logger.info(f"Arquivo {local_zip} já existe, pulando extração.")
        
        logger.info(f"Extraindo {local_zip}")
        with zipfile.ZipFile(local_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        os.remove(local_zip)
    else:
        logger.info(f"Arquivo {local_csv_path} já existe, pulando download e extração.")
            
    

    # Encontrar o arquivo CSV
    csv_pattern = os.path.join(extract_dir, "DADOS", "MICRODADOS_ENEM_*.csv")
    csv_files = glob.glob(csv_pattern)

    if not csv_files:
        raise FileNotFoundError(f"Nenhum MICRODADOS_ENEM encontrado em {csv_pattern}")
    
    local_csv_path = csv_files[0]
    logger.info(f"CSV localizado: {local_csv_path}")

    # Caminho no HDFS
    hdfs_csv_path = f"/user/enem/csv_raw/{year}/MICRODADOS_ENEM_{year}.csv"
    logger.info(f"Enviando CSV para HDFS em {hdfs_csv_path}")

    # Copia arquivo local para o HDFS com subprocess (modo simples)
    subprocess.run(["hdfs", "dfs", "-mkdir", "-p", os.path.dirname(hdfs_csv_path)], check=False)
    res = subprocess.run(["hdfs", "dfs", "-put", "-f", local_csv_path, hdfs_csv_path], capture_output=True, text=True)

    if res.returncode != 0:
        logger.error(f"❌ Falha ao enviar CSV para o HDFS:\n{res.stderr}")
        raise RuntimeError("Erro ao executar hdfs dfs -put")
    else:
        logger.info("✅ CSV enviado para o HDFS com sucesso.")
     
    return hdfs_csv_path


# Spark Session
spark = SparkSession.builder \
    .appName("ENEM Pipeline") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "2g") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

# Schema enxuto
schema = StructType([
    StructField("NU_INSCRICAO", LongType(), True),
    StructField("NU_ANO", IntegerType(), True),
    StructField("SG_UF_PROVA", StringType(), True),
    StructField("TP_ESCOLA", IntegerType(), True),
    StructField("Q006", StringType(), True),
    StructField("NU_NOTA_MT", DoubleType(), True)
])

# Mapas auxiliares
renda_map = {
    "A": 300, "B": 500, "C": 900, "D": 1300, "E": 1900, "F": 2500, "G": 3200,
    "H": 3900, "I": 4600, "J": 5400, "K": 6300, "L": 7200, "M": 8100,
    "N": 9100, "O": 10200, "P": 11500
}
state_region = {
    "AC":"Norte","AM":"Norte","AP":"Norte","PA":"Norte","RO":"Norte","RR":"Norte","TO":"Norte",
    "AL":"Nordeste","BA":"Nordeste","CE":"Nordeste","MA":"Nordeste","PB":"Nordeste","PE":"Nordeste","PI":"Nordeste","RN":"Nordeste","SE":"Nordeste",
    "DF":"Centro-Oeste","GO":"Centro-Oeste","MT":"Centro-Oeste","MS":"Centro-Oeste",
    "ES":"Sudeste","MG":"Sudeste","RJ":"Sudeste","SP":"Sudeste",
    "PR":"Sul","RS":"Sul","SC":"Sul"
}

# UDFs
@F.udf("int")
def renda_valor(code): return renda_map.get(code, 0)

@F.udf("string")
def uf_regiao(uf): return state_region.get(uf, "Indefinido")

# Acumulador
df_all = None
total_records = 0

for year in YEARS:
    t0 = time.time()

    # ETAPA 1 - DOWNLOAD E LEITURA
    hdfs_csv_path = download_and_extract(year)
    logger.info(f"Lendo CSV via HDFS: {hdfs_csv_path}")
    df = spark.read.csv(f"{HDFS_URI}{hdfs_csv_path}", sep=";", header=True, encoding="ISO-8859-1", schema=schema)

    df.repartition(10).write.mode("overwrite").option("header", True).csv(f"{HDFS_URI}/user/enem/csv/{year}")
    df = df.withColumn("Q006_VALOR", renda_valor(F.col("Q006")))
    df = df.withColumn("REGIAO", uf_regiao(F.col("SG_UF_PROVA"))).dropna(subset=["NU_NOTA_MT", "Q006_VALOR"])

    total_records += df.count()

    # ETAPA 2 - SALVAR PARQUET LOCAL + HDFS
    local_out = f"{LOCAL_PARQUET_BASE}/{year}"
    hdfs_out = f"{HDFS_URI}/user/enem/parquet/{year}"
    df.write.mode("overwrite").parquet(hdfs_out)

    df = df.withColumn("ANO", F.lit(year))
    df_all = df_all.unionByName(df) if df_all else df

    logger.info(f"Tempo total {year}: {round(time.time() - t0, 2)} segundos")

# ETAPA 3 - ANÁLISES COMPLEXAS
logger.info("Executando análises...")

# 1. Média por UF/ano
df_uf = df_all.groupBy("ANO", "SG_UF_PROVA").agg(F.avg("NU_NOTA_MT").alias("MEDIA_MT"))

# 2. Correlação renda vs nota por ano
correlacoes = []
for year in YEARS:
    df_y = df_all.filter(F.col("ANO") == year)
    corr = df_y.stat.corr("Q006_VALOR", "NU_NOTA_MT")
    correlacoes.append((year, corr))
df_corr = spark.createDataFrame(correlacoes, ["ANO", "CORR_Q006_MT"])

# 3. Média por tipo de escola
df_escola = df_all.groupBy("ANO", "TP_ESCOLA").agg(F.avg("NU_NOTA_MT").alias("MEDIA_MT"))

# 4. Disparidades regionais (média e desvio)
df_regiao = df_all.groupBy("REGIAO").agg(
    F.avg("NU_NOTA_MT").alias("MEDIA_MT"),
    F.stddev("NU_NOTA_MT").alias("STD_MT"),
    F.count("*").alias("NUM_ESTUDANTES")
)

# 5. Faixas de renda
df_faixa = df_all.withColumn("FAIXA_RENDA", F.when(F.col("Q006_VALOR") <= 1000, "Até 1k")
                                            .when(F.col("Q006_VALOR") <= 3000, "1k–3k")
                                            .when(F.col("Q006_VALOR") <= 6000, "3k–6k")
                                            .otherwise("Acima de 6k")) \
                 .groupBy("ANO", "FAIXA_RENDA").agg(F.avg("NU_NOTA_MT").alias("MEDIA_MT"))

# ETAPA 4 - SALVAR RESULTADOS
def salvar(df, nome):
    df.write.mode("overwrite").parquet(f"{HDFS_URI}/user/enem/resultados/{nome}")

salvar(df_uf, "media_por_uf")
salvar(df_corr, "correlacao_renda")
salvar(df_escola, "media_por_escola")
salvar(df_regiao, "desigualdade_regiao")
salvar(df_faixa, "media_por_faixa_renda")

# ETAPA FINAL - MÉTRICAS
end_total = time.time()
logger.info("✅ Pipeline finalizado")
logger.info(f"⏱️ Tempo total de execução: {round(end_total - start_total, 2)}s")
logger.info(f"📊 Total de registros processados: {total_records}")

spark.read.parquet(f"{HDFS_URI}/user/enem/resultados/media_por_uf").show()
spark.read.parquet(f"{HDFS_URI}/user/enem/resultados/media_por_escola").show()
spark.read.parquet(f"{HDFS_URI}/user/enem/resultados/correlacao_renda").show()
spark.read.parquet(f"{HDFS_URI}/user/enem/resultados/desigualdade_regiao").show()
spark.read.parquet(f"{HDFS_URI}/user/enem/resultados/media_por_faixa_renda").show()