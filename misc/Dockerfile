FROM bitnami/spark:latest

USER root

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz && \
    tar -xzf hadoop-3.3.6.tar.gz && \
    mv hadoop-3.3.6 /opt/hadoop && \
    ln -s /opt/hadoop/bin/hdfs /usr/local/bin/hdfs && \
    rm hadoop-3.3.6.tar.gz

RUN pip install requests

RUN mkdir -p /opt/spark/jobs

COPY src/main.py /opt/spark/jobs/main.py

RUN chmod +x /opt/spark/jobs/main.py

WORKDIR /opt/spark/jobs

CMD ["/bin/bash"]
