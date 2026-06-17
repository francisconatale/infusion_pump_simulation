FROM python:3.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    build-essential

RUN git clone https://github.com/capocchi/PythonPDEVS.git && \
    cd PythonPDEVS/src && \
    python setup.py install

# Comando por defecto para correr tu simulación automáticamente
CMD ["python", "main.py"]
