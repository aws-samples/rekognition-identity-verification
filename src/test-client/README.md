# Test Client

This command line interface (CLI) supports testing the User Portal functionality.

Most operations require the caller specifies the **CloudFormation Stack Name** (`riv_stack_name`) and **region** you are testing.

The `riv_stack_name` is specifies which instance (Prod, Dev, ...) you want to target, and is specified during the [one-click.sh](../../one-click.sh) invocation.

If you do not specify the value, it defaults to **Riv-Prod**.

## How do I use the test-client

```sh
# Optional/Recommended create a virtual enviroment (removes need for sudo)
virtualenv .env

# Activate this the virtual environment
source .env/bin/activate 

# Install dependencies
pip3 install -r src/test-client/requirements.txt

# Confirm the client starts
python3 src/test-client/app.py help
```

## What permissions does this tool require

The caller must have `ssm:GetParameter*` rights to the resources `/riv/{stack-name}/userportal/url`.

This requirement is due to the `get_userportal_address` dynamically fetching the endpoints.

## How do I register a new user

Developers can create new users with any of the following examples.

It is not supported to register the "same face" multiple times under different **UserId**.

```sh
# Register the user nbachmei from a local image 
python3 ./app.py register -z Riv-Prod -r ca-central-1 -u nbachmei -p ./faces/nbachmei.jpg

# Register the user nbachmei with properties from an idcard
python3 ./app.py register-idcard -z Riv-Prod -r ca-central-1 -u nbachmei -p ./faces/nbachmei.jpg -c ./faces/private/license.jpg
```

## How do I update an existing user

Developers can update existing users with any of the following examples.

It is not supported to update a user before calling register.  The service also checks that the new face is comparable (e.g., 95% confidence) to the registration photo.

```sh
# Update the user data
python3 ./app.py update -z Riv-Prod -r ca-central-1 -u nbachmei -p ./faces/different.jpg
```

## How do I authenticate a user

Developers can perform an authentication check with any of the following examples.

It is not supported to authenticate the user before calling register.

```sh
# Update the user data
python3 ./app.py auth -z Riv-Prod -r ca-central-1 -u nbachmei -p ./faces/nbachmei.jpg
```

## How do I generate payloads for external tooling

Developers can export valid payloads with any of the following examples.

```sh
# Generate a random payload to stdout
python3 ./app.py encode -o -

# Write a random payload to a file
python3 ./app.py encode -o payload.json

# Write a local data
python3 ./app.py encode -o payload.json -u nbachmei -p ./faces/nbachmei.jpg

# Register the payload with curl
curl -X POST -H "Content-Type: application/json" https://your-apigateway-address/register --data "@payload.json"
```
