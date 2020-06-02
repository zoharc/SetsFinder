# Sets Crawler

## Overview
This is the set crawler - is uses a rabbitMQ queue and crawls mixcloud:
- for each set message it receives, it adds the set to the sets DB and adds all the users who liked this set to the queue (as user message)
- for each user message, if finds the sets the user liked and adds them to the queue (as set message)

## Running with Docker

To run the server on a Docker container, first create a queue using:
```bash
# running the queue
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 --network="host"  rabbitmq:3-management

#building the docker
docker build -t swagger_server .

# starting up a container
docker run -p 8080:8080  -e URL_TO_APPEND_SETS='URL' --network="host" --name MixcloudCrawler sets_crawler
# if a local sets_finder is running, the url should be http://localhost:8080/v1/insertSetDetails'
```

Then add a sets message to the queue called MixcloudMessages, and the crawller will start from it

