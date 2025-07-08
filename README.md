
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
#### Dataset completo:
```bash
wget https://download.inep.gov.br/microdados/microdados_enem_2020.zip
wget https://download.inep.gov.br/microdados/microdados_enem_2021.zip
wget https://download.inep.gov.br/microdados/microdados_enem_2023.zip
unzip microdados_enem_2020.zip -d data/enem_data/2020/
unzip microdados_enem_2021.zip -d data/enem_data/2021/
unzip microdados_enem_2023.zip -d data/enem_data/2023/
```

## 3. How to install and run

> Totalmente containerizado com Docker + Docker Swarm

### 3.1 Quick start

```bash
docker build -t enem-spark-job -f docker/Dockerfile .

docker-compose up --scale spark-worker=2 --scale datanode=1 -d 
```
Spark-Worker e Datanode definem a quantidade de nós com spark-work e datanode

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

> NumberOfCores - 6 
> NumberOfLogicalProcessors - 12
> RAM - 16GM

### 6.2 What did you test?

- Variação de workers/datanodes
- Métricas: tempo, throughput, CPU/RAM (docker stats)

### 6.3 Results

#### Testes por configuração de workers/datanodes

| Configuração | Tempo (s) | Registros    | Throughput (linhas/s) | CPU Total (%) | RAM média (MB) | Threads por worker |
|--------------|-----------|--------------|------------------------|----------------|----------------|---------------------|
| 1W / 1D      | 415.66    | 7.535.711    | 18.129,37              | 50.0%          | 4096           | 3.0                 |
| 2W / 1D      | 362.80    | 7.535.711    | 20.770,75              | 50.0%          | 4096           | 3.0                 |
| 2W / 2D      | 365.82    | 7.535.711    | 20.599,35              | 50.0%          | 4096           | 3.0                 |

A partir de 3 workers tivemos problema de RAM para a execução do Job

#### Análise realizadas

As seguintes análises estatísticas foram realizadas sobre os dados do ENEM (anos 2020, 2021 e 2023), com persistência dos resultados em HDFS:

#### 📊 1. Média Geral por UF

Exemplo de destaques (2020):
- São Paulo (SP): **541,20**
- Minas Gerais (MG): **534,08**
- Acre (AC): **480,82**
- Amapá (AP): **476,80**

#### 🏫 2. Média por Tipo de Escola (`TP_ESCOLA`) (2020)

| Tipo de Escola | Descrição                  | Média ENEM |
|----------------|----------------------------|------------|
| 1              | Não respondeu              | 520.03     |
| 2              | Pública                    | 499.52     |
| 3              | Privada                    | 610.63     |

> Observa-se desempenho significativamente maior entre estudantes oriundos de escolas privadas e do exterior.

#### 💰 3. Correlação entre Renda Familiar (`Q006`) e Nota de Matemática

| Ano  | Correlação (Pearson) |
|------|----------------------|
| 2020 | 0.3945               |
| 2021 | 0.3745               |
| 2023 | 0.3824               |

> A correlação positiva mostra que, quanto maior a renda, maior tende a ser a nota em matemática.

#### 🌎 4. Desigualdade Regional

| Região       | Média     | Desvio Padrão | N° Estudantes |
|--------------|-----------|----------------|----------------|
| Sudeste      | 559.36    | 123.15         | 2.531.820      |
| Sul          | 550.79    | 119.85         | 813.382        |
| Centro-Oeste | 528.26    | 121.08         | 627.912        |
| Nordeste     | 508.94    | 115.88         | 2.744.535      |
| Norte        | 487.11    | 103.82         | 818.062        |

> As regiões Norte e Nordeste apresentam as menores médias e menor dispersão.

#### 📈 5. Média por Faixa de Renda

| Faixa de Renda | Média ENEM |
|----------------|------------|
| Até 1k         | 490.49     |
| 1k–3k          | 544.49     |
| 3k–6k          | 598.89     |
| Acima de 6k    | 650.86     |

> Existe uma clara progressão positiva entre renda familiar e desempenho em matemática.

---

Todos os resultados foram salvos no HDFS na camada `resultados`, em formato Parquet

## 7. Discussion and conclusions

- ✅ Pipeline robusto e escalável
- ⚠️ Desafios com permissões HDFS e alocação de memória

## 8. References and external resources

- [Microdados ENEM - INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados)
- [Apache Spark](https://spark.apache.org/)
- [Docker Swarm](https://docs.docker.com/engine/swarm/)
- [BDE Hadoop Docker](https://github.com/big-data-europe/docker-hadoop)
- [Bitnami Spark Docker](https://hub.docker.com/r/bitnami/spark)
