FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY requirements.txt ./
COPY . . 

RUN pip3 install -r requirements.txt

RUN chmod +x entrypoint.sh

EXPOSE 8000

COPY entrypoint.sh .
ENTRYPOINT ["sh", "entrypoint.sh"]
