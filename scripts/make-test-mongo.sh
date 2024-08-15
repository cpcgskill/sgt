docker stop some-mongo
docker rm some-mongo
docker run --name some-mongo -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=BOQfXt8uW0oCtVnCKHmc -p 9586:27017 -d mongo