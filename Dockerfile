FROM python:3.8

# install deps
RUN apt update && apt install -y ffmpeg
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# move in application
WORKDIR /app
COPY ./*py /app/
COPY ./static/ /app/static/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
