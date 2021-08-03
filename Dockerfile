FROM python:3
ENV PYTHONUNBUFFERED=1

RUN apt-get update

WORKDIR /usr/src/app
COPY requirements.txt ./
ADD . /usr/src/app/
RUN pip install -r requirements.txt
RUN python manage.py migrate

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]