docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker build -t hotmaps/building-hc .
docker run --name building-hc -p 9006:80 -d hotmaps/building-hc
