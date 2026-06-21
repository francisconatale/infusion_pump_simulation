FROM python:3.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    build-essential

RUN git clone https://github.com/capocchi/PythonPDEVS.git && \
    cd PythonPDEVS/src && \
    python setup.py install

COPY . .

RUN pip install --timeout 300 -r requirements.txt -v

CMD python main.py && python src/analysis/plotter.py