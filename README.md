
# IoT Prototyping Project: Tracker Web Backend

## How to run (with docker)

We assume that you have make, docker and docker-compose installed.

If you run the command below command, it will create a new database and the python application, listening on localhost:8080.
It will reload on any code changes, but you need to restart it if you add a dependency.

```sh
make docker-run
```

If you want to run unit tests (also inside docker):

```sh
make docker-test
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
