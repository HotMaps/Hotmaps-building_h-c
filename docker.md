show log of currently running container:  
```docker logs -f `docker ps | tail -n +2 | cut -d " " -f 1` ```

open a shell on the currently running container:  
```docker exec -it "`docker ps | tail -n +2 | cut -d " " -f 1"` bash ```
