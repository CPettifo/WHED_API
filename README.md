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

Ensure that you have setup environment variables with correct configuration
for your development environment (see .env.example). The service attempt to
will load from a .env if the file is present.

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
# login (returns an access token)
curl --request POST \
  --url http://localhost:7071/api/login \
  --header 'content-type: application/json' \
  --data '{
  "username": "test@example.com",
  "password": "zenziW-koxzo0-fuxhuc"
}'
```

```bash
# get a list of currencies
curl --request GET \
  --url http://localhost:7071/api/currency \
  --header 'Authorization: Bearer <copy-access-token-from-login-call>'
```

```bash
# add new currency record
curl --request POST \
  --url http://localhost:7071/api/currency \
  --header 'Authorization: Bearer <copy-access-token-from-login-call>' \
  --header 'content-type: application/json' \
  --data '{
  "currency_code": "TST",
  "currency_name": "TEST"
}'
```

```bash
# delete the currency with code TST
curl --request DELETE \
  --url http://localhost:7071/api/currency/TST \
  --header 'Authorization: Bearer <copy-access-token-from-login-call>'
```

### Run the tests

```bash
python -m unittest test_function_app.py
```


### Deployment

This project follows established, standard patterns for Azure Cloud Functions using Python, so deployment guides are readily available from Microsoft.

#### Configure Azure Cloud Function

Follow the guide [here](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-function-app-portal?pivots=programming-language-python) to create the serverless function.

Or update your organizations infrastructure codebase (Azure Resource Manager, Terraform, Pulumi etc) so that the cloud function is managed by your organizations IaC tool of choice.

#### Application Settings

We recommend using [Application Settings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings?tabs=azure-portal%2Cto-premium) to inject the environment variables for each deployment environment. See `.env.example` file for a list of required environment variables.

Secrets can be stored in [Key Vault](https://azure.microsoft.com/en-au/products/key-vault) and [referenced in application settings](https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references?tabs=azure-cli).

#### Continuous Deployment

We recommend GitOps / Github actions for ongoing deployments to Azure. A full guide can be found [here](https://learn.microsoft.com/en-us/azure/azure-functions/functions-how-to-github-actions?tabs=linux%2Cdotnet&pivots=method-cli).