docker cp app/. "$(docker ps -a -q):/data"
docker restart $(docker ps -a -q)
