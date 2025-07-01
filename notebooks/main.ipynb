# enem_pipeline.py
import os
import requests
import zipfile
import logging
import time
import glob
import subprocess
from pyspark.sql import SparkSession, functions as F, types as T

# Configuração global
YEARS = [2020, 2021, 2023]
HDFS_URI = "hdfs://namenode:8020"
HDFS_RAW_BASE = "/enem/raw"
HDFS_PROCESSED_BASE = "/enem/processed"
LOCAL_DATA_DIR = "/data/enem_data"
PARQUET_LOCAL_DIR = "/data/enem_clean"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ENEMPipeline")

# Função para baixar e extrair microdados
def download_and_extract(year):
    url = f"https://download.inep.gov.br/microdados/microdados_enem_{year}.zip"
    zip_path = f"enem{year}.zip"
    extract_path = os.path.join(LOCAL_DATA_DIR, str(year))

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
        logger.info(f"Baixando {url}...")
        r = requests.get(url, stream=True)
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
        logger.info("Extraindo...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        os.remove(zip_path)
    return extract_path

# Envia para HDFS
def upload_to_hdfs(local_dir, hdfs_dir):
    subprocess.run(["hdfs", "dfs", "-mkdir", "-p", hdfs_dir], check=False)
    for file in glob.glob(f"{local_dir}/**/*.csv", recursive=True):
        subprocess.run(["hdfs", "dfs", "-put", "-f", file, hdfs_dir])
        logger.info(f"Enviado {file} para HDFS")

# Spark Session otimizada
def get_spark():
    return SparkSession.builder \
        .appName("EnemPipeline") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()

# Limpeza e conversão para Parquet
def process_data(year, csv_file):
    spark = get_spark()
    df = spark.read.option("header", True).option("sep", ";").csv(csv_file)

    df_clean = df.dropna(subset=["NU_NOTA_MT", "NU_NOTA_CN"]) \
               .withColumn("NU_NOTA_MT", F.col("NU_NOTA_MT").cast("double")) \
               .withColumn("NU_NOTA_CN", F.col("NU_NOTA_CN").cast("double"))

    parquet_path = f"{PARQUET_LOCAL_DIR}/{year}"
    df_clean.write.mode("overwrite").parquet(parquet_path)

    df_clean.write.mode("overwrite").parquet(f"{HDFS_URI}{HDFS_PROCESSED_BASE}/{year}")
    logger.info(f"Processamento finalizado para {year}")

# Análise: correlação

def analise_correlacao(year):
    spark = get_spark()
    df = spark.read.parquet(f"{HDFS_URI}{HDFS_PROCESSED_BASE}/{year}")
    df.select("NU_NOTA_MT", "NU_NOTA_CN").summary().show()
    correl = df.corr("NU_NOTA_MT", "NU_NOTA_CN")
    logger.info(f"Correlação entre Matemática e Ciências da Natureza em {year}: {correl:.2f}")

if __name__ == "__main__":
    start = time.time()
    for year in YEARS:
        local = download_and_extract(year)
        upload_to_hdfs(local, f"{HDFS_URI}{HDFS_RAW_BASE}/{year}")
        csv_file = glob.glob(f"{local}/**/MICRODADOS_ENEM_{year}.csv", recursive=True)[0]
        process_data(year, csv_file)
        analise_correlacao(year)
    logger.info(f"Tempo total: {time.time() - start:.2f}s")