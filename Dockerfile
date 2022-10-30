FROM python:3.7

ENV TZ="Europe/Moscow"


EXPOSE 3306

RUN mkdir /bot
WORKDIR /bot

COPY requirements.txt /bot/requirements.txt
RUN pip install -r requirements.txt
COPY . /bot

CMD ./startup.sh
