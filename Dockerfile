FROM python:3.12-alpine
ENV HOME=/home/app
ENV PYTHONUNBUFFERED=1
WORKDIR $HOME
COPY requirements.txt  ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
