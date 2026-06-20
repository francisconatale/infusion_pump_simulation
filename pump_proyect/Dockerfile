FROM python:3.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    build-essential

RUN git clone https://github.com/capocchi/PythonPDEVS.git && \
    cd PythonPDEVS/src && \
    python setup.py install

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]