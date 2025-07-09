
# Final project report: Pipeline de Big Data do ENEM com Spark e Docker Swarm

## 1. Context and motivation

O principal objetivo deste projeto é processar e analisar grandes volumes de dados educacionais, especificamente os microdados do ENEM, utilizando tecnologias de Big Data. Buscamos resolver o problema de análise eficiente de dados massivos (13+ milhões de registros anuais) para extrair insights sobre desigualdade educacional no Brasil.

O foco está na construção de um pipeline escalável e distribuído que possa:
- Processar automaticamente múltiplos anos de dados do ENEM (2020, 2021, 2023)
- Realizar análises estatísticas complexas sobre correlações socioeconômicas
- Demonstrar a viabilidade de infraestrutura containerizada para Big Data
- Responder perguntas importantes sobre disparidades regionais e socioeconômicas na educação brasileira

A motivação é demonstrar como tecnologias modernas de Big Data podem ser aplicadas para gerar evidências que subsidiem políticas públicas educacionais baseadas em dados.

## 2. Data

### 2.1 Detailed description

**Fonte dos dados:**
- **Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP)**
- Link oficial: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados

**Conteúdo dos dados:**
- Microdados do ENEM dos anos de 2020, 2021 e 2023
- **Volume total**: Aproximadamente 13+ milhões de registros distribuídos em:
  - ENEM 2020: ~5 milhões de candidatos
  - ENEM 2021: ~3 milhões de candidatos  
  - ENEM 2023: ~3+ milhões de candidatos
- **Características por registro**:
  - Centenas de atributos por candidato
  - Informações socioeconômicas detalhadas (renda familiar, escolaridade dos pais, etc.)
  - Localização geográfica (estado onde realizou a prova)
  - Notas por área de conhecimento (Ciências da Natureza, Ciências Humanas, Linguagens e Códigos, Matemática)
  - Tipo de escola (pública/privada)
  - Dados demográficos

**Formato dos dados:**
- Arquivos CSV delimitados por ponto e vírgula (;)
- Codificação ISO-8859-1
- Compactados em arquivos ZIP (~500MB-1.5GB cada arquivo)
- Tamanho total descompactado: ~15GB

### 2.2 How to obtain the data

**Amostra de dados (obrigatória):**
Uma pequena amostra dos dados está incluída na pasta `datasample/enem_sample.csv` deste repositório. Esta amostra contém 15 registros representativos (tamanho < 1KB) e é obrigatória para permitir testes rápidos do projeto.

**Dataset completo:**
Para obter o dataset completo (não incluído no repositório), use os comandos abaixo:

```bash
# Download automático via wget
wget https://download.inep.gov.br/microdados/microdados_enem_2020.zip
wget https://download.inep.gov.br/microdados/microdados_enem_2021.zip
wget https://download.inep.gov.br/microdados/microdados_enem_2023.zip
```

**Observação importante:** O pipeline realiza download automático dos dados durante a execução. Não é necessário baixar manualmente os arquivos, exceto se desejar pré-carregar os dados. Se os arquivos ZIP estiverem presentes na raiz do projeto, o pipeline os utilizará automaticamente.

## 3. How to install and run

> Observação: O projeto é totalmente compatível com uma instalação padrão do Docker e usa apenas contêineres Docker para execução. Nenhuma ferramenta externa ou instalação adicional é necessária — este é um requisito estrito.

### 3.1 Quick start (usando dados de amostra em `datasample/`)

Execute o projeto imediatamente usando Docker com os comandos exatos abaixo:

**Linux/macOS:**
```bash
# Tornar scripts executáveis
chmod +x bin/*.sh

# Executar pipeline completo
./bin/run.sh
```

**Windows:**
```cmd
# Executar pipeline completo
bin\run.bat
```

**Alternativa manual usando Docker Compose:**
```bash
# Construir imagem Docker
docker build -t enem-spark-job -f misc/Dockerfile .

# Executar com Docker Compose
cd misc
docker-compose up --scale spark-worker=2 --scale datanode=1 -d
```

### 3.2 Como executar com o dataset completo

Para usar o dataset completo (em vez da amostra padrão):

1. **Opção 1 (Automática)**: Execute normalmente. O pipeline baixará automaticamente os dados do INEP.

2. **Opção 2 (Manual)**: Baixe os arquivos ZIP e coloque na raiz do projeto:
   ```bash
   wget https://download.inep.gov.br/microdados/microdados_enem_2020.zip
   wget https://download.inep.gov.br/microdados/microdados_enem_2021.zip
   wget https://download.inep.gov.br/microdados/microdados_enem_2023.zip
   ```

O pipeline detectará automaticamente os arquivos presentes e os utilizará.

## 4. Project architecture

O sistema possui uma arquitetura distribuída baseada em contêineres Docker que implementa um pipeline completo de Big Data:

```
[Dados INEP (ZIP)] 
       ↓
[Download/Extração Automática]
       ↓
[HDFS] ←→ [Cluster Spark (PySpark)]
       ↓
[Resultados em HDFS: Parquet + Métricas]
```

### Principais componentes e interações:

**1. Camada de Dados:**
- **Fonte**: Arquivos ZIP dos microdados ENEM do INEP
- **Ingestão**: Download e extração automática pelo container spark-job
- **Armazenamento**: HDFS distribuído (namenode + datanodes)

**2. Camada de Processamento:**
- **spark-master**: Coordenador do cluster Spark
- **spark-worker[n]**: Nós de processamento distribuído (escaláveis)
- **spark-job**: Container da aplicação PySpark principal

**3. Camada de Armazenamento:**
- **namenode**: Servidor de metadados do HDFS
- **datanode[n]**: Nós de armazenamento distribuído (escaláveis)

**4. Fluxo de dados:**
1. Container `spark-job` baixa dados do INEP
2. Dados são extraídos e carregados no HDFS
3. Spark processa dados distribuídos através dos workers
4. Resultados analíticos são salvos em formato Parquet no HDFS
5. Métricas de performance são coletadas em tempo real

**Execução em contêineres:**
- Todos os componentes executam em contêineres Docker isolados
- Comunicação via rede interna `hadoop`
- Volume compartilhado `./data` para persistência local
- Escalabilidade horizontal via Docker Compose scaling

**Interfaces de monitoramento:**
- **Spark Master UI**: http://localhost:8080 (monitoramento do cluster)
- **HDFS NameNode UI**: http://localhost:9870 (sistema de arquivos)

## 5. Workloads evaluated

Este projeto avalia três principais cargas de trabalho no contexto de processamento de Big Data:

**[WORKLOAD-1] Ingestão de Dados:**
- **Descrição**: Download, extração e carregamento de arquivos CSV massivos (>500MB cada) para o HDFS
- **Operações específicas**:
  - Download automático de arquivos ZIP do INEP via HTTPS
  - Extração de arquivos comprimidos (descompressão)
  - Transferência para HDFS usando API Hadoop
  - Criação de estrutura hierárquica de diretórios
- **Métricas avaliadas**: Tempo de download, throughput de transferência, utilização de rede

**[WORKLOAD-2] Transformação e Enriquecimento de Dados:**
- **Descrição**: Limpeza, normalização e engenharia de features em milhões de registros
- **Operações específicas**:
  - Normalização de colunas numéricas (remoção de caracteres especiais)
  - Mapeamento de códigos categóricos para valores numéricos (renda familiar)
  - Filtragem de registros inválidos e duplicados
  - Criação de features derivadas (regiões geográficas)
  - Reparticionamento otimizado para paralelismo
- **Métricas avaliadas**: Registros processados por segundo, utilização de CPU/memória

**[WORKLOAD-3] Análises Estatísticas Complexas:**
- **Descrição**: Agregações complexas, correlações e consultas analíticas multi-anuais
- **Operações específicas**:
  - Cálculos de médias por agrupamentos (UF, tipo de escola, região)
  - Correlações de Pearson entre variáveis numéricas
  - Análises de desvio padrão e dispersão
  - Operações de join entre datasets de diferentes anos
  - Criação de faixas categóricas e análises de distribuição
- **Métricas avaliadas**: Tempo de execução de queries, throughput analítico, eficiência de agregações

## 6. Experiments and results

## 6. Experiments and results

### 6.1 Experimental environment

Os experimentos foram executados em um ambiente com as seguintes especificações:

**Configuração de Hardware:**
- **CPU**: 6 cores físicos, 12 processadores lógicos
- **RAM**: 16 GB DDR4
- **Armazenamento**: SSD NVMe
- **OS**: Ambiente de contêineres Linux via Docker no Windows

**Stack de Software:**
- **Apache Spark**: 3.x (distribuição Bitnami)
- **Hadoop HDFS**: 3.2.1
- **Python**: 3.8+
- **Docker**: Versão estável mais recente
- **Docker Compose**: v2.x

### 6.2 What did you test?

Realizamos testes abrangentes de performance variando diferentes configurações de infraestrutura:

**Parâmetros testados:**
1. **Escalabilidade computacional**: Número de Spark workers (1, 2, 3+)
2. **Escalabilidade de armazenamento**: Número de HDFS datanodes (1, 2)
3. **Alocação de recursos**: Memória e CPU por worker

**Métricas coletadas:**
- **Tempo de execução**: Tempo total end-to-end (wall-clock time)
- **Throughput**: Registros processados por segundo
- **Utilização de recursos**: CPU e memória por worker
- **Latência**: Tempo de resposta para operações individuais
- **Métricas de aplicação**: Número de partições, shuffle operations

**Configurações testadas:**
- **Baseline**: 1 Worker + 1 DataNode
- **Escala computacional**: 2 Workers + 1 DataNode  
- **Escala storage**: 2 Workers + 2 DataNodes
- **Limitação de recursos**: 3+ Workers (limitado por RAM disponível)

**Replicações**: Cada configuração foi executada uma vez com dataset completo devido ao tempo de execução (~6-7 horas por experimento). O pipeline coleta métricas contínuas durante a execução para garantir consistência.

### 6.3 Results

#### Tabela de Performance por Configuração

| Configuração | Tempo (s) | Registros   | Throughput (reg/s) | CPU Total (%) | RAM Média (MB) | Threads/Worker |
|--------------|-----------|-------------|-------------------|---------------|----------------|----------------|
| 1W / 1D      | 415,66    | 7.535.711   | 18.129,37         | 50,0%         | 4.096          | 3,0            |
| 2W / 1D      | 362,80    | 7.535.711   | 20.770,75         | 50,0%         | 4.096          | 3,0            |
| 2W / 2D      | 365,82    | 7.535.711   | 20.599,35         | 50,0%         | 4.096          | 3,0            |

A partir de 3 workers tivemos problema de RAM para a execução do Job

**Análise dos resultados de performance:**

1. **Melhor configuração**: 2 Workers + 1 DataNode apresentou o melhor desempenho
2. **Ganho de throughput**: ~14% de melhoria ao escalar de 1 para 2 workers  
3. **Limitação de recursos**: Memória se torna fator limitante além de 2 workers
4. **Escalabilidade de storage**: DataNodes adicionais mostram impacto mínimo na performance

**O que aprendemos:**
- A configuração ótima para nosso ambiente é 2W/1D
- O gargalo principal é memória, não CPU ou armazenamento
- O paralelismo horizontal é efetivo até o limite de recursos
- HDFS scaling tem retornos decrescentes para este workload

#### Resultados Analíticos dos Dados ENEM

O pipeline processou com sucesso 7,5+ milhões de registros do ENEM, gerando insights educacionais abrangentes:

**📊 1. Performance Acadêmica por Estado (Amostra 2020):**
- São Paulo (SP): 541,20 pontos (maior média)
- Minas Gerais (MG): 534,08 pontos  
- Acre (AC): 480,82 pontos
- Amapá (AP): 476,80 pontos (menor média)

*Diferença de 64,4 pontos entre estados extremos revela disparidades significativas.*

**🏫 2. Performance por Tipo de Escola (2020):**
| Tipo | Descrição    | Média ENEM |
|------|-------------|------------|
| 2    | Pública     | 499,52     |
| 3    | Privada     | 610,63     |

*Vantagem de 111 pontos para escolas privadas demonstra desigualdade no sistema educacional.*

**💰 3. Correlação Renda vs Matemática:**
| Ano  | Correlação Pearson |
|------|--------------------|
| 2020 | 0,3945             |
| 2021 | 0,3745             |
| 2023 | 0,3824             |

*Correlação positiva consistente (~0,38) confirma impacto da renda no desempenho.*

**🌎 4. Desigualdade Regional:**
| Região      | Média  | Desvio | Estudantes |
|-------------|--------|--------|------------|
| Sudeste     | 559,36 | 123,15 | 2.531.820  |
| Norte       | 487,11 | 103,82 | 818.062    |

*Diferença de 72 pontos entre regiões extremas evidencia desigualdade geográfica.*

## 7. Discussion and conclusions

### O que funcionou bem:

**✅ Implementação técnica bem-sucedida:**
- Pipeline robusto e escalável processando 7,5+ milhões de registros
- Aquisição automática de dados de fontes externas
- Processamento distribuído eficiente com Apache Spark e HDFS
- Tratamento abrangente de erros e mecanismos de recuperação
- Coleta de métricas de performance em tempo real
- Containerização completa garantindo reprodutibilidade

**✅ Insights educacionais relevantes:**
- Confirmação quantitativa da correlação entre fatores socioeconômicos e desempenho acadêmico
- Evidências claras de desigualdades regionais e por tipo de escola
- Dados que podem subsidiar políticas públicas educacionais

### Desafios e limitações:

**⚠️ Desafios técnicos encontrados:**
- Complexidades de configuração e permissões do HDFS em ambiente containerizado
- Limitações de alocação de memória restringindo escalabilidade horizontal
- Gargalos de I/O de rede durante transferência de datasets grandes
- Problemas de timing de orquestração de contêineres durante inicialização
- Dependência de conectividade de internet para download de dados

**⚠️ Limitações do trabalho:**
- Ambiente de teste limitado a uma única máquina (não cluster real)
- Análises focadas em correlações básicas (sem modelos preditivos avançados)
- Testes de performance limitados devido ao tempo de execução

### Conclusões:

Este projeto demonstra com sucesso a viabilidade de infraestrutura containerizada de Big Data para análises educacionais. O pipeline processa efetivamente dados do ENEM em larga escala, fornecendo insights valiosos sobre o cenário educacional brasileiro.

**Principais contribuições:**
1. **Técnica**: Prova de conceito de pipeline Big Data totalmente containerizado
2. **Analítica**: Quantificação de desigualdades educacionais brasileiras
3. **Metodológica**: Template reproduzível para análises similares

A forte correlação entre fatores socioeconômicos e desempenho acadêmico revelada por nossa análise reforça a importância de abordar a desigualdade educacional através de intervenções políticas baseadas em evidências.

## 8. References and external resources

**Fontes de dados:**
- [Microdados ENEM - INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados) - Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira

**Tecnologias e ferramentas:**
- [Apache Spark](https://spark.apache.org/) - Framework de processamento distribuído
- [Apache Hadoop HDFS](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html) - Sistema de arquivos distribuído
- [Docker](https://docs.docker.com/) - Plataforma de containerização
- [Docker Compose](https://docs.docker.com/compose/) - Orquestração de multi-contêineres

**Imagens Docker utilizadas:**
- [Bitnami Spark Docker](https://hub.docker.com/r/bitnami/spark) - Imagem base do Spark
- [BDE Hadoop Docker](https://github.com/big-data-europe/docker-hadoop) - Imagens do ecossistema Hadoop

**Bibliotecas Python:**
- [PySpark](https://spark.apache.org/docs/latest/api/python/index.html) - API Python para Apache Spark
- [Requests](https://requests.readthedocs.io/) - Cliente HTTP para Python

**Documentação e tutoriais:**
- [Spark Programming Guide](https://spark.apache.org/docs/latest/programming-guide.html)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [HDFS Commands Guide](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/CommandsManual.html)
