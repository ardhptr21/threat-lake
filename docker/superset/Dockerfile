FROM apache/superset:4.0.2

USER root

COPY docker/superset/superset_config.py /app/pythonpath/superset_config.py
COPY docker/superset/bootstrap.sh /app/bootstrap.sh

RUN chmod +x /app/bootstrap.sh

ENV SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

USER superset

CMD ["/app/bootstrap.sh"]

