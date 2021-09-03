FROM python:3.8.10-slim-buster
COPY requirements.txt crypto.py /
RUN pip install -r requirements.txt
CMD [ "python", "./crypto.py" ]
