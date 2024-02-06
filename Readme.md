### revving technical test

This is set up to work from docker compose, so assuming that you  have docker and docker compose installed.

It should set up a django application server, a postgres database, a redis server and a celery worker. 

Make sure nothing is blocking port 8000 (or change the docker-compose.yml)

`git pull`

 followed by

```cd revving``` 

To run the tests 

```
docker compose   -f docker-compose-tests.yml up --build
```

Then `ctrl` + `c` to stop the docker containers.


To run the application server:

 ```docker compose up --build``` 
 

You should then be able to access the application in a web browser on [127.0.0.1:8000/upload/](127.0.0.1:8000/upload/)


If there is an error that the tables are not created run
`docker compose run -rm migrate`
(Though this should run as part of the main docker file setup)

The endpoints are:

[127.0.0.1:8000/upload/](127.0.0.1:8000/upload/)
[127.0.0.1:8000/totals/](127.0.0.1:8000/totals/)

The endpoints will work as webpages or json requests. You can Add the accept header, or add '?format=json' 
to the querystring to get a json response.

You can post a file to the upload endpoint

`curl -F "csv_file=@<path_to_csv_file>" http://127.0.0.1:8000/upload/ -H "Accept: application/json"`

`curl -F "csv_file=@<path_to_csv_file>" http://127.0.0.1:8000/upload/?format=json`

and get totals with 

`curl 127.0.0.1:8000/totals/ -H "Accept: application/json"`
or 
`curl 127.0.0.1:8000/totals/?format=json` 



## Still todo 
- round the totals to two decimal places in JSON
- convert the query to use Django F expressions, then can add filtering and sorting more easily
- run the ingestion as a celery task
- Add CSFR tokens
- improve error messages
- input data directly as json (probably add in DRF and serialzers)
- add more tests
- add ENUM for currencies
- more data validation

## also, I made a number of assumptions, 
- that the currency stays the same betweem customer and revenue source
- that the fees stay the same month to month
 