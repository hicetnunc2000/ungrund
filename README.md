# ungrund

decentralized api

```
docker image build -t storage-flask:1.0 .
docker container run --publish 5000:5000 --detach --name sf storage-flask:1.0
```

delete container:
```
docker container rm --force sf
```

# routes

access: https://localhost:5000/
you'll find all routes documented

# next updates


- integration with ledgers
- FA1.2
- auto documentation/detection of contract's entrypoints
- cryptographed requests/responses

# donate
```
eth: 0xa0290385540aB98222d00547cb59a9E72A788Bf3
tz: tz1L6qEvhRFufA5KES6QJ48pvgvTrLcGUoLb
```
