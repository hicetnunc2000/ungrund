FROM python:latest

RUN pip install --upgrade pip

RUN apt-get update \
&& apt-get install -y libsodium-dev \
libsecp256k1-dev \
libgmp-dev \
pkg-config

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python"]
CMD ["app.py"]