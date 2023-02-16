FROM python:alpine
WORKDIR /rdaq-server
COPY . /rdaq-server/
RUN pip install -r requirements.txt
CMD python main.py