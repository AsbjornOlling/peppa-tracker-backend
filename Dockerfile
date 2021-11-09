FROM python:3.8

# install deps
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# move in application
WORKDIR /app
COPY ./*py /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
