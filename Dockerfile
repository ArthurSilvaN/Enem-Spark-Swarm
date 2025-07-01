# Dockerfile - Container com Spark + Hadoop client + dependências Python

FROM bitnami/spark:latest

USER root

# Instala dependências do sistema e do Python
RUN apt-get update && \
    apt-get install -y curl unzip wget python3-pip netcat-openbsd && \
    pip install --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instala Hadoop client (para comandos HDFS funcionarem)
RUN wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz && \
    tar -xzf hadoop-3.3.6.tar.gz && \
    mv hadoop-3.3.6 /opt/hadoop && \
    ln -s /opt/hadoop/bin/hdfs /usr/local/bin/hdfs && \
    rm hadoop-3.3.6.tar.gz

# Configura variáveis de ambiente
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin
ENV HADOOP_USER_NAME=root

# Instala dependências Python para análises
COPY docker/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Copia jobs Python para dentro do container
COPY jobs/ /opt/spark/jobs/

WORKDIR /opt/spark/jobs