FROM python:3.10-slim-buster
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
WORKDIR /app
COPY . /app
RUN pip --no-cache-dir install -r requirements.txt
CMD ["flask", "run" "--host", "0.0.0.0"]
EXPOSE 8080
