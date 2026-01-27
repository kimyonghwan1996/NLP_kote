FROM apache/spark:3.5.0

USER root

# Python & pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# SQLite JDBC 드라이버 다운로드
RUN mkdir -p /opt/jars && \
    curl -L -o /opt/jars/sqlite-jdbc.jar \
    https://repo1.maven.org/maven2/org/xerial/sqlite-jdbc/3.45.1.0/sqlite-jdbc-3.45.1.0.jar

# Python libs
RUN pip install --no-cache-dir --default-timeout=200 pyspark==3.5.0 sparknlp pandas tqdm sqlite-utils
RUN pip install --no-cache-dir --default-timeout=200 transformers
RUN pip install --no-cache-dir --default-timeout=200 torch


WORKDIR /app
