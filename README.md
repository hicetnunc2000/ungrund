# ungrund oracle

Ungrund Oracle v1.0.0 enables you to make HTTP Requests for a microsservice which interacts with the Tezos Blockchain. It provides you multiple routes in which you can configure it's sessions, making possible users interactions to happen with FA1.2 Standard Tokens and other Smart Contracts. presented on the Tezos + CoinList Hackaton.


# requirements
```
Docker version 19.03.9 and Docker Machine version 0.16.2
```

# build
```
docker image build -t ungrund:1.0 .
docker container run --publish 5000:5000 --detach --name ungrund ungrund:1.0
```

delete container
```
docker container rm --force ungrund
```

# routes

access: https://localhost:5000/
you'll find routes documented

you should first visit key route and configure it with your wallet credentials

# next updates

- venv
- forge operations
- FA2
- modules fabric
- cryptographed requests/responses

# references
```
https://gitlab.com/tzip/tzip/-/blob/master/proposals/tzip-7/ManagedLedger.tz (FA1.2)
https://github.com/tqtezos/lorentz-contract-oracle
https://medium.com/@hicetnunc2000/ungrund-oracle-34d1fe0659a3
https://medium.com/tqtezos/oracles-on-tezos-1f0a085a1eda
https://tezos.foundation/wrapping-up-tezos-coinlist-hackathon/
```
# contracts

https://better-call.dev/carthagenet/KT1Syeu2hxMEhAareV5pB3RRiaJJA5hs3Aym/operations

