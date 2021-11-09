
# IoT Prototyping Project: Tracker Web Backend

## How to run (with docker)

We assume that you have docker and docker-compose installed.

If you run this command, it will create a new database and the python application.
It should reload on any code changes:

```sh
docker-compose up
```

If you want to run unit tests (inside docker):

```sh
make test
```

## How to run (without docker)

First, install the python dependencies with pip:

```sh
pip install -r requirements.txt
```

Then, you need to run a mongodb database.
By default, the application will connect to `mongodb://localhost`, which should be the default for mongo.

Then, assuming you already have make/cmake installed, just run:

```sh
make
```

This will host the python web application on port https://localhost:8000.
You can access it from the browser now.
It *should* watch for changes to the python files, and reload the application whenever necessary.
