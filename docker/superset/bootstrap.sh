#!/bin/sh
set -eu

superset db upgrade
superset fab create-admin \
  --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
  --firstname "${SUPERSET_ADMIN_FIRSTNAME:-Superset}" \
  --lastname "${SUPERSET_ADMIN_LASTNAME:-Admin}" \
  --email "${SUPERSET_ADMIN_EMAIL:-admin@threatlake.local}" \
  --password "${SUPERSET_ADMIN_PASSWORD:-admin}" || true
superset init
superset run -h 0.0.0.0 -p 8088

