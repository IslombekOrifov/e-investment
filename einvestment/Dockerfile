FROM python:3.10.4
ADD . /app
WORKDIR /app
COPY . .

RUN apt-get update -y
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
# #RUN apt-get install python3 -y
#RUN apt-get install python3-pip -y
RUN python3 -m pip install --upgrade pip
#RUN python3 -m pip install --upgrade setuptools

#RUN apt-get install -y netcat
#RUN apt-get install sudo ufw build-essential libpq-dev libmysqlclient-dev python3-venv python3-dev default-libmysqlclient-dev libpython3-dev -y
#RUN apt-get install ffmpeg libsm6 libxext6 -y

RUN python3 -m pip install -r requirements.txt
RUN pip3 install django-crontab
#RUN pip3 install requests-toolbelt
#RUN pip3 install requests-async
#RUN pip3 install aiohttp
#RUN pip3 install thread6

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
