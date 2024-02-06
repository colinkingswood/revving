### revving technical test

This is set up to work from docker compose, so assuming that you  have docker and docker compose installed.

Make sure nothing is blocking port 8000 (or change teh docker-compose.yml)

`git pull`

 followed by

```cd revving``` 

followed by 

 ```docker compose up --build``` 
 
should work

You should then be able to access the application in a web browser on [127.0.0.1:8000/upload/](127.0.0.1:8000/upload/)


If there is an error that the tables are not created run
```docker compose run -rm migrate
```




 