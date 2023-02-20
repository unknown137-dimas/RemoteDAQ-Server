FROM python:alpine
WORKDIR /rdaq-server
COPY . /rdaq-server/
RUN apk add openssh-client && python -m pip install --upgrade pip && pip install -r requirements.txt
CMD python main.py