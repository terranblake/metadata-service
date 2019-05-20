FROM python:3.7-alpine as base
FROM base as builder

RUN mkdir /install
WORKDIR /install

RUN apk add --update curl gcc g++ && rm -rf /var/cache/apk/*
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

COPY requirements.txt /requirements.txt
RUN pip install --upgrade setuptools
RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY src /app
WORKDIR /app

EXPOSE 5000
CMD ["python", "server.py"]