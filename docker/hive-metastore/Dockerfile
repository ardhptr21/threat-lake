FROM apache/hive:4.0.0

USER root

# Add Hadoop S3 JARs
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget -O /opt/hive/lib/hadoop-aws-3.3.4.jar https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    wget -O /opt/hive/lib/aws-java-sdk-bundle-1.12.262.jar https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

COPY docker/hive-metastore/hive-site.xml /opt/hive/conf/hive-site.xml

USER hive

EXPOSE 9083

CMD ["hive", "--service", "metastore"]
