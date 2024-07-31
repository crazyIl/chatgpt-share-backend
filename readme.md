# ChatGPT Share Backend Docker Setup

This README provides instructions on how to run the ChatGPT Share Backend using Docker with either MySQL or SQLite as the database. Follow the steps below to get started.

### Environment Variables

| Variable            | Default Value               | Required | Description                                       |
|---------------------|-----------------------------|----------|---------------------------------------------------|
| `FUCLAUDE_BASE_URL` |`https://demo.fuclaude.com`  | Y        | Base URL for the FUCLAUDE API.                    |
| `DB_HOST`           |                             | N        | Hostname or IP address of the MySQL server.       |
| `DB_PORT`           |                             | N        | Port number of the MySQL server.                  |
| `DB_USER`           |                             | N        | Username for the MySQL database.                  |
| `DB_PASSWORD`       |                             | N        | Password for the MySQL database.                  |
| `DB_NAME`           |                             | N        | Name of the MySQL database.                       |
| `SITE_PASSWORD`     |                             | Y        | Password for accessing the site.                  |

### Volume Mapping

| Container Directory | Description                          |
|---------------------|--------------------------------------|
| `/app/data`         | Directory to store SQLite database.  |

## How to Run

1. **Ensure Docker is installed** on your system.
2. **Choose your preferred database**: MySQL or SQLite.
3. **Prepare the required environment variables**.
4. **Run the appropriate Docker command** from above.
5. **Access the application** at `http://<your-docker-host>:5000`.

## Example

For a MySQL setup, replace the placeholders with your actual database details and run:

```sh
docker run -d --restart always -p 5000:5000 --name chatgpt-share-backend \
-e FUCLAUDE_BASE_URL=https://demo.fuclaude.com \
-e DB_HOST=172.17.0.1 \
-e DB_PORT=3306 \
-e DB_USER=myuser \
-e DB_PASSWORD=mypassword \
-e DB_NAME=mydatabase \
-e SITE_PASSWORD=mysecretpassword \
crazyl/chatgpt-share-backend:latest
```

For an SQLite setup, ensure the directory `/opt/chatgpt-share-backend/data` exists on your host system, and then run:

```sh
docker run -d --restart always -p 5000:5000 --name chatgpt-share-backend \
-e FUCLAUDE_BASE_URL=https://demo.fuclaude.com \
-v /opt/chatgpt-share-backend/data:/app/data \
-e SITE_PASSWORD=mysecretpassword \
crazyl/chatgpt-share-backend:latest
```

That's it! Your ChatGPT Share Backend should now be up and running.

# ChatGPT Share Backend API Documentation

This documentation provides details on the API endpoints available for managing and using tokens in the ChatGPT Share Backend. The endpoints allow you to upload, use, refresh, delete, and list tokens.

## API Endpoints

### Upload Token

Uploads a new token to the backend.

**Endpoint:**
```
POST /api/share/config/{site_password}/token
```

**Request:**
```sh
curl --location 'http://<your-docker-host>:5000/api/share/config/{site_password}/token' \
--header 'Content-Type: application/json' \
--data '{
    "type": "openai",
    "refresh_token": "",
    "access_token": "",
    "prefix": "rd",
    "assign_to": "",
    "email": "",
    "remark": ""
}'
```

**Parameters:**

| Parameter       | Type   | Description                                           |
|-----------------|--------|-------------------------------------------------------|
| `type`          | String | Type of the token (e.g., `openai`,`claude`).          |
| `refresh_token` | String | Refresh token value (conditional).                    |
| `access_token`  | String | Access token value (conditional).                     |
| `prefix`        | String | Prefix for the token (optional).                      |
| `assign_to`     | String | Assign the token to a specific user key (optional).   |
| `email`         | String | Email associated with the token (optional).           |
| `remark`        | String | Additional remarks about the token (optional).        |

### Use Token

Logs in using a user key with the specified token type.

**Endpoint:**
```
GET /api/share/auth/{token_type}/login_user_key?user_key={user_key}
```

**Request:**
```sh
curl --location 'http://<your-docker-host>:5000/api/share/auth/{token_type}/login_user_key?user_key={user_key}'
```

**Parameters:**

| Parameter     | Type   | Description                                      |
|---------------|--------|--------------------------------------------------|
| `token_type`  | String | Type of the token (`fuclaude` or `openai`).      |
| `user_key`    | String | User key for logging in.                         |

**Examples:**
```sh
curl --location 'http://<your-docker-host>:5000/api/share/auth/fuclaude/login_user_key?user_key=rd_123'
curl --location 'http://<your-docker-host>:5000/api/share/auth/openai/login_user_key?user_key=rd_123'
```

### Delete Token

Deletes a specified token.

**Endpoint:**
```
DELETE /api/share/config/{site_password}/token/{token_id}
```

**Request:**
```sh
curl --location --request DELETE 'http://<your-docker-host>:5000/api/share/config/{site_password}/token/{token_id}'
```

**Parameters:**

| Parameter   | Type   | Description                      |
|-------------|--------|----------------------------------|
| `token_id`  | String | The ID of the token to delete.   |

### List Tokens

Retrieves a list of all tokens.

**Endpoint:**
```
GET /api/share/config/{site_password}/token/list
```

**Request:**
```sh
curl --location 'http://<your-docker-host>:5000/api/share/config/{site_password}/token/list'
```

## Example Usage

### Uploading a Token
```sh
curl --location 'http://<your-docker-host>/api/share/config/{site_password}/token' \
--header 'Content-Type: application/json' \
--data '{
    "type": "openai",
    "refresh_token": "",
    "access_token": "",
    "prefix": "rd",
    "assign_to": "",
    "email": "",
    "remark": ""
}'
```

### Using a Token
```sh
curl --location 'http://<your-docker-host>:5000/api/share/auth/openai/login_user_key?user_key=rd_123'
```

### Deleting a Token
```sh
curl --location --request DELETE 'http://<your-docker-host>:5000/api/share/config/{site_password}/token/1'
```

### Listing Tokens
```sh
curl --location 'http://<your-docker-host>:5000/api/share/config/{site_password}/token/list'
```
