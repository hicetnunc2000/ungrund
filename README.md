# ungrund

descentralized api

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
you`ll find all routes documented

# next updates:

- code scalability updates
- integration with wallets
- auto documentation of contract's entrypoints