FROM python:3.6
MAINTAINER Joseph Walton <joseph.walton@ons.gov.uk>

WORKDIR /app
COPY . /app
EXPOSE 8083
RUN pip3 install -r requirements.txt --upgrade

ENTRYPOINT ["python3", "-m", "ras_api_gateway"]