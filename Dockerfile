FROM python:3.7

EXPOSE 3306

RUN mkdir /bot
WORKDIR /bot

COPY requirements.txt /bot/requirements.txt
RUN pip install -r requirements.txt
COPY . /bot

CMD ./startup.sh
