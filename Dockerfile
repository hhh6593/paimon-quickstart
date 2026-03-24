FROM flink:1.19.3-java17

ARG PAIMON_VERSION=1.3.1
ARG FLINK_SHORT=1.19

# S3 plugin 활성화 (이미 번들된 JAR를 plugins 디렉토리에서 lib로 복사)
RUN mkdir -p /opt/flink/plugins/s3-fs-hadoop && \
    cp /opt/flink/opt/flink-s3-fs-hadoop-*.jar /opt/flink/plugins/s3-fs-hadoop/ && \
    curl -L -o /opt/flink/lib/paimon-flink-${FLINK_SHORT}-${PAIMON_VERSION}.jar \
      https://repo1.maven.org/maven2/org/apache/paimon/paimon-flink-${FLINK_SHORT}/${PAIMON_VERSION}/paimon-flink-${FLINK_SHORT}-${PAIMON_VERSION}.jar; \
    curl -L -o /opt/flink/lib/paimon-s3-${PAIMON_VERSION}.jar \
      https://repo1.maven.org/maven2/org/apache/paimon/paimon-s3/${PAIMON_VERSION}/paimon-s3-${PAIMON_VERSION}.jar; \
    curl -L -o /opt/flink/lib/flink-shaded-hadoop-2-uber-2.8.3-10.0.jar \
      https://repo1.maven.org/maven2/org/apache/flink/flink-shaded-hadoop-2-uber/2.8.3-10.0/flink-shaded-hadoop-2-uber-2.8.3-10.0.jar; \
    curl -L -o /opt/flink/lib/flink-sql-connector-kafka-3.3.0-1.19.jar \
      https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.19/flink-sql-connector-kafka-3.3.0-1.19.jar; \
    chown flink:flink /opt/flink/lib/*.jar