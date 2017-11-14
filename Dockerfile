FROM python:3.6
MAINTAINER Joseph Walton <joseph.walton@ons.gov.uk>

WORKDIR /app
COPY . /app
EXPOSE 8083
RUN pip install pipenv==8.3.1 && pipenv install --deploy --system

ENTRYPOINT ["python", "-m", "ras_api_gateway"]