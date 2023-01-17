FROM python:alpine
WORKDIR /rdaq-server
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
CMD python main.py