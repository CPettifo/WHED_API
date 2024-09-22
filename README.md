## WHED API - Proof of Concept

This API is a proof of concept that a copy of the WHED can be accessed securely using an API, with user authentication and configuration of queries from the user. This is the capstone project for several students at the University of New England in Australia and is being developed in collaboration with the International Association of Universities and UNESCO.

Contributors will be credited in the NOTICE file.

### Setup

macOS project setup

```bash
# install tools
brew tap azure/functions
brew install azure-functions-core-tools@4
curl https://pyenv.run | bash

# install python
pyenv install 3.11

# setup venv
python -m venv .venv

# activate venv
source .venv/bin/activate

# install requirements into venv
pip install -r requirements.txt
```

### Running locally

```bash
# run with azure-function-core-tools
func start
```

### testing locally

##### Use a testing client
```bash
# install / use testing program

# eg. install bruno
brew install bruno
# if using bruno - then import the collection at ./bruno/une-test
```

```yaml
# test user credentials
user: test@example.com
password: zenziW-koxzo0-fuxhuc
```

##### Example requests

```bash
curl --request POST \
  --url http://localhost:7071/api/login \
  --header 'content-type: application/json' \
  --data '{
  "username": "test@example.com",
  "password": "zenziW-koxzo0-fuxhuc"
}'
```

```bash
curl --request GET \
  --url http://localhost:7071/api/currency \
  --header 'Authorization: Bearer <copy-access-token-from-login-call>'
```


