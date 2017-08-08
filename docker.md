`docker logs -f \`docker ps | tail -n +2 | cut -d " " -f 1\``
`docker exec -it "\`docker ps | tail -n +2 | cut -d " " -f 1"\` bash`
