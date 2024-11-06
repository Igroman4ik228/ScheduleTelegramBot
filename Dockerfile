FROM python:3.12
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade setuptools && \
    pip install -r requirements.txt

COPY . .

RUN chmod -R 755 /app
