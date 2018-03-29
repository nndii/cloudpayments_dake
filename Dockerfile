FROM python:3.6

WORKDIR /app
COPY ./ /app

RUN pip3 install gunicorn && \
    python3 setup.py install

EXPOSE 4911
CMD ["gunicorn", "cp_fake:create_app()", \
    "--bind=0.0.0.0:4911", \
    "--worker-class=aiohttp.GunicornWebWorker"]