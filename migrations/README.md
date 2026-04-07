Migración inicial incluida como referencia operativa.

Para una evolución real del proyecto:
1. flask db init
2. flask db migrate -m "initial schema"
3. flask db upgrade

En esta versión 5.1 el arranque usa `python init_db.py` para simplificar
la puesta en marcha local y en Docker.
