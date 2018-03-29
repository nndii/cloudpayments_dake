FROM python:3.6

WORKDIR /app
COPY ./ /app

RUN pip3 install gunicorn && \
    python3 setup.py install

CMD ["gunicorn", "cp_fake:create_app()", \
    "--bind=0.0.0.0:4949", \
    "--worker-class=aiohttp.GunicornWebWorker", \
    "--access-logfile=-", "--log-level=debug", \
    "--error-logfile=-"]
