
# Final project report: ENEM Big Data Pipeline with Spark and Docker Swarm

## 1. Context and motivation

O principal objetivo deste projeto é processar e analisar grandes volumes de dados educacionais, especificamente os microdados do ENEM, utilizando tecnologias de Big Data. O foco está na construção de um pipeline escalável, capaz de lidar com mais de 13 milhões de registros por ano, com análises que correlacionam desempenho com fatores socioeconômicos e geográficos. A motivação está em demonstrar a viabilidade de se usar infraestrutura distribuída (via Docker Swarm e Apache Spark) para responder a perguntas importantes sobre desigualdade educacional no Brasil.

## 2. Data

### 2.1 Detailed description

- **Fonte:** Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP)  
  - Link oficial: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados

- **Conteúdo:**  
  - Microdados do ENEM dos anos de 2020, 2021 e 2023.
  - Cada arquivo contém mais de 10 milhões de registros e centenas de atributos:
    - Informações socioeconômicas dos candidatos
    - Localização da prova (UF)
    - Notas por área (ex: matemática)

- **Formato:** Arquivos CSV compactados em ZIP.

### 2.2 How to obtain the data

#### Sample:
- Localizado em: `datasample/MICRODADOS_ENEM_SAMPLE.csv`
- Contém 1MB com dados de 2020.

#### Dataset completo:
```bash
wget https://download.inep.gov.br/microdados/microdados_enem_2020.zip
wget https://download.inep.gov.br/microdados/microdados_enem_2021.zip
wget https://download.inep.gov.br/microdados/microdados_enem_2023.zip
unzip microdados_enem_2020.zip -d data/enem_data/2020/
```

## 3. How to install and run

> Totalmente containerizado com Docker + Docker Swarm

### 3.1 Quick start

```bash
docker compose up --build --scale spark-worker=1 --scale datanode=1 -d
docker exec -it <nome_container_spark-job> python3 /opt/spark/jobs/main.py
```

### 3.2 Full dataset

- Monte a pasta `data/` com os arquivos ZIP.
- O script baixa, extrai, envia ao HDFS e analisa automaticamente.

## 4. Project architecture

```
[INEP ZIP Files] 
      ↓
[Downloader + Extractor]
      ↓
[HDFS] ←→ [Spark Job Container (PySpark)]
      ↓
[Resultados em HDFS: Parquet + Métricas]
```

### Componentes:

- `spark-master` / `spark-worker[n]`: Spark distribuído.
- `namenode` / `datanode[n]`: HDFS.
- `spark-job`: script PySpark.
- Volume compartilhado `./data`.

## 5. Workloads evaluated

- **[WORKLOAD-1] Ingestão**
- **[WORKLOAD-2] Transformação e enriquecimento**
- **[WORKLOAD-3] Análises estatísticas**

## 6. Experiments and results

### 6.1 Experimental environment

> VM com 6 vCPUs, 12GB RAM, Ubuntu 22.04, Docker 24.0.5

### 6.2 What did you test?

- Variação de workers/datanodes
- Métricas: tempo, throughput, CPU/RAM (docker stats)

### 6.3 Results

| Configuração       | Tempo (s) | Registros | Throughput | CPU (%) | RAM (MB) |
|--------------------|-----------|-----------|------------|---------|----------|
| 1W / 1D            | 199.23    | 13.1M     | 65801.7    | 52%     | 920 MB   |
| 2W / 2D            | 211.87    | 13.1M     | 61855.3    | 39%     | 880 MB   |
| 3W / 2D            | 224.67    | 13.1M     | 58339.7    | 28%     | 770 MB   |

## 7. Discussion and conclusions

- ✅ Pipeline robusto e escalável
- ⚠️ Desafios com permissões HDFS e alocação de memória
- 📉 Overhead ao aumentar workers (troca entre nós)

## 8. References and external resources

- [Microdados ENEM - INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados)
- [Apache Spark](https://spark.apache.org/)
- [Docker Swarm](https://docs.docker.com/engine/swarm/)
- [BDE Hadoop Docker](https://github.com/big-data-europe/docker-hadoop)
- [Bitnami Spark Docker](https://hub.docker.com/r/bitnami/spark)
