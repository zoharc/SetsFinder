# Python Set Finder

## Overview
This is the Set Finder - this project can find sets by artists and by other sets (using the artists from those sets)
This endpoint can also insert set details into the db


## Usage
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt
MYSQL_HOST_URI='MYSQL_HOST_URI' MYSQL_USER='USER' MYSQL_PASSWD='PASS' python3 -m swagger_server 
```

and open your browser to here:

```
http://localhost:8080/sets
http://localhost:8080/artists
```

The service endpoints definitioncan be found here:

```
http://localhost:8080/v1/swagger.json
```

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t sets_finder .

# starting up a container
docker run -p 8080:8080 -e MYSQL_HOST_URI='MYSQL_HOST_URI' -e MYSQL_USER='USER' -e MYSQL_PASSWD='PASS' sets_finder
```