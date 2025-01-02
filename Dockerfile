FROM python:3.12

RUN useradd -m bso
WORKDIR /home/bso

RUN mkdir /var/bso \
    /var/bso/sql \
    /var/bso/logs \ 
    /var/bso/database

ENV BSO_SQL_PATH=/var/bso/sql \
    BSO_DB_PATH=/var/bso/database/.sqlite3 \
    BSO_LOGS_PATH=/var/bso/logs/ \
    HOST=0.0.0.0 \
    PORT=8000 \
    LOG_LEVEL=30
    
RUN chown bso:bso /var/bso -R
USER bso

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY sql/ ${BSO_SQL_PATH}

COPY src/ .

CMD python -m uvicorn main:app --host $HOST --port $PORT --reload
