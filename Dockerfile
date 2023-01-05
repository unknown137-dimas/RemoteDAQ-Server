FROM python:alpine
RUN pip install -r requirements.txt
CMD python main.py