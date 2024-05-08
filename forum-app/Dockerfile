FROM python:3.10

WORKDIR /app
EXPOSE 5000

RUN groupadd -g 1000 systemadmin && useradd -m -u 1000 -g 1000 -s /bin/bash -d /app systemadmin

COPY ./entrypoint.sh /entrypoint.sh
COPY ./wait-for-psql.py /usr/local/bin/wait-for-psql.py
COPY ./requirements.txt /requirements.txt

RUN chmod +x /usr/local/bin/wait-for-psql.py /entrypoint.sh 

RUN pip install --upgrade pip && pip install -r /requirements.txt

# copy everyting from this dir to /app inside image/container
COPY . .

USER systemadmin
WORKDIR /app
VOLUME ["/app"]

# what command to run when container starts
ENTRYPOINT ["/entrypoint.sh"]
CMD ["flask"]

