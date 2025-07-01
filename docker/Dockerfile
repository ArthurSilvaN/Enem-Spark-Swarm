FROM bitnami/spark:latest

USER root

# Atualiza pacotes do sistema e instala dependências necessárias
RUN install_packages curl unzip python3-pip && \
    apt-get update && \
    apt-get upgrade -y && \
    pip install --upgrade pip

COPY docker/requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copia o script principal para dentro da imagem
COPY main.py /opt/spark/jobs/main.py

WORKDIR /opt/spark/jobs

CMD ["/bin/bash"]
