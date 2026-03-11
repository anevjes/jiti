# SDK Proxy API Contract

**Feature**: api1  
**Date**: 2026-03-11  
**Component**: /apis/api1/sdk-proxy

---

## Base URL

These are the recommended base URLs for the SDK proxy that fronts the Petstore API.

- **Local (developer workstation)**:  
  `http://localhost:8080/api1`

- **Debug / Integration (shared)**:  
  `https://debug.example.com/api1`

> All endpoint paths below are relative to this SDK proxy base URL.  
> The SDK proxy forwards to the upstream Petstore server: `https://petstore3.swagger.io/api/v3`.

---

## Endpoints

### Add Pet

```
POST /pet
```

Create a new pet in the store by forwarding the provided `Pet` payload to the upstream Petstore `/pet` endpoint.

**Forwarding rules**

- Method: `POST`
- Upstream URL: `https://petstore3.swagger.io/api/v3/pet`
- Auth:
  - If SDK client is configured with OAuth token, forward as `Authorization: Bearer <token>`.
  - Otherwise, call is made without authentication (for sandboxes only, inferred).
- Headers:
  - Forward `Content-Type`, `Accept`, and `Authorization` (if present).
  - Add `X-SDK-Client: api1` (inferred).
- Body:
  - Forward JSON/XML/form body as-is.
- Query params: none.

#### Path parameters

None.

#### Request body

`Pet` (JSON / XML / x-www-form-urlencoded)

Minimal example (JSON):

```json
{
  "id": 10,
  "name": "doggie",
  "category": {
    "id": 1,
    "name": "Dogs"
  },
  "photoUrls": [
    "https://example.com/photos/dog1.jpg"
  ],
  "tags": [
    {
      "id": 100,
      "name": "puppy"
    }
  ],
  "status": "available"
}
```

#### Success responses

| HTTP | Condition                            | Body schema |
|------|--------------------------------------|-------------|
| 200  | Pet created successfully             | `Pet`       |

#### Error responses

| HTTP | Condition                     | Notes                                   |
|------|-------------------------------|-----------------------------------------|
| 400  | Invalid input                 | Upstream validation failure             |
| 422  | Validation exception          | Business/field-level validation error   |
| 5xx  | Unexpected error (default)    | Network or upstream failure (inferred)  |

#### Example – cURL

```bash
curl -X POST "http://localhost:8080/api1/pet" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "id": 10,
    "name": "doggie",
    "category": { "id": 1, "name": "Dogs" },
    "photoUrls": ["https://example.com/photos/dog1.jpg"],
    "tags": [{ "id": 100, "name": "puppy" }],
    "status": "available"
  }'
```

#### Example – HTTP exchange

**Request**

```http
POST /api1/pet HTTP/1.1
Host: localhost:8080
Content-Type: application/json
Accept: application/json

{
  "id": 10,
  "name": "doggie",
  "category": { "id": 1, "name": "Dogs" },
  "photoUrls": ["https://example.com/photos/dog1.jpg"],
  "tags": [{ "id": 100, "name": "puppy" }],
  "status": "available"
}
```

**Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 10,
  "name": "doggie",
  "category": { "id": 1, "name": "Dogs" },
  "photoUrls": ["https://example.com/photos/dog1.jpg"],
  "tags": [{ "id": 100, "name": "puppy" }],
  "status": "available"
}
```

---

### Update Pet

```
PUT /pet
```

Update an existing pet in the store by sending a full `Pet` object (including its `id`).

**Forwarding rules**

- Method: `PUT`
- Upstream URL: `https://petstore3.swagger.io/api/v3/pet`
- Same auth and header semantics as **Add Pet**.
- Body is forwarded unchanged.

#### Path parameters

None.

#### Request body

`Pet` (must include `id` of the pet to update).

Example:

```json
{
  "id": 10,
  "name": "doggie v2",
  "category": { "id": 1, "name": "Dogs" },
  "photoUrls": ["https://example.com/photos/dog1-v2.jpg"],
  "tags": [{ "id": 101, "name": "adult" }],
  "status": "sold"
}
```

#### Success responses

| HTTP | Condition                | Body schema |
|------|--------------------------|-------------|
| 200  | Pet updated successfully | `Pet`       |

#### Error responses

| HTTP | Condition              |
|------|------------------------|
| 400  | Invalid ID supplied    |
| 404  | Pet not found          |
| 422  | Validation exception   |
| 5xx  | Unexpected error       |

#### Example – cURL

```bash
curl -X PUT "http://localhost:8080/api1/pet" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "id": 10,
    "name": "doggie v2",
    "category": { "id": 1, "name": "Dogs" },
    "photoUrls": ["https://example.com/photos/dog1-v2.jpg"],
    "tags": [{ "id": 101, "name": "adult" }],
    "status": "sold"
  }'
```

---

### Find Pets by Status

```
GET /pet/findByStatus
```

Retrieve pets filtered by status.

**Forwarding rules**

- Method: `GET`
- Upstream URL: `https://petstore3.swagger.io/api/v3/pet/findByStatus`
- Query params:
  - `status` (required; enum: `available`, `pending`, `sold`) forwarded as-is. Multiple comma-separated values supported.
- Headers:
  - Forward `Accept`, `Authorization` (if present).
- No body.

#### Path parameters

None.

#### Query parameters

| Name   | In    | Type   | Required | Description                                          |
|--------|-------|--------|----------|------------------------------------------------------|
| status | query | string | yes      | `available`, `pending`, or `sold` (comma-separated) |

#### Success responses

| HTTP | Condition             | Body schema     |
|------|-----------------------|-----------------|
| 200  | Pets returned         | `Pet[]` (array) |

#### Error responses

| HTTP | Condition             |
|------|-----------------------|
| 400  | Invalid status value  |
| 5xx  | Unexpected error      |

#### Example – cURL

```bash
curl -X GET "http://localhost:8080/api1/pet/findByStatus?status=available" \
  -H "Accept: application/json"
```

#### Example response

```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "id": 10,
    "name": "doggie",
    "category": { "id": 1, "name": "Dogs" },
    "photoUrls": ["https://example.com/photos/dog1.jpg"],
    "tags": [{ "id": 100, "name": "puppy" }],
    "status": "available"
  }
]
```

---

### Find Pets by Tags

```
GET /pet/findByTags
```

Retrieve pets that match any of the provided tags.

**Forwarding rules**

- Method: `GET`
- Upstream URL: `https://petstore3.swagger.io/api/v3/pet/findByTags`
- Query params:
  - `tags` (required; array of strings) forwarded with `explode=true`, i.e. `?tags=tag1&tags=tag2` or comma-separated.
- Headers: forward `Accept`, `Authorization`.

#### Path parameters

None.

#### Query parameters

| Name | In    | Type       | Required | Description                            |
|------|-------|------------|----------|----------------------------------------|
| tags | query | string[]   | yes      | Tags to filter by                      |

#### Success responses

| HTTP | Condition     | Body schema |
|------|---------------|-------------|
| 200  | Pets returned | `Pet[]`     |

#### Error responses

| HTTP | Condition            |
|------|----------------------|
| 400  | Invalid tag value    |
| 5xx  | Unexpected error     |

#### Example – cURL

```bash
curl -X GET "http://localhost:8080/api1/pet/findByTags?tags=puppy&tags=small" \
  -H "Accept: application/json"
```

#### Example response

```json
[
  {
    "id": 11,
    "name": "tiny dog",
    "category": { "id": 1, "name": "Dogs" },
    "photoUrls": ["https://example.com/photos/dog2.jpg"],
    "tags": [
      { "id": 100, "name": "puppy" },
      { "id": 101, "name": "small" }
    ],
    "status": "available"
  }
]
```

---

### Get Pet by ID

```
GET /pet/{petId}
```

Return a single pet by its identifier.

**Forwarding rules**

- Method: `GET`
- Upstream URL: `https://petstore3.swagger.io/api/v3/pet/{petId}`
- Path parameter `petId` mapped 1:1.
- Headers: forward `Accept`, `api_key` (if configured), `Authorization`.
- No body.

#### Path parameters

| Name  | In   | Type    | Required | Description        |
|-------|------|---------|----------|--------------------|
| petId | path | int64   | yes      | ID of pet to fetch |

#### Success responses

| HTTP | Condition         | Body schema |
|------|-------------------|-------------|
| 200  | Pet found         | `Pet`       |

#### Error responses

| HTTP | Condition            |
|------|----------------------|
| 400  | Invalid ID supplied  |
| 404  | Pet not found        |
| 5xx  | Unexpected error     |

#### Example – cURL

```bash
curl -X GET "http://localhost:8080/api1/pet/10" \
  -H "Accept: application/json" \
  -H "api_key: YOUR_API_KEY"
```

#### Example response

```json
{
  "id": 10,
  "name": "doggie",
  "category": { "id": 1, "name": "Dogs" },
  "photoUrls": ["https://example.com/photos/dog1.jpg"],
  "tags": [{ "id": 100, "name": "puppy" }],
  "status": "available"
}
```

---

### Update Pet with Form Data

```
POST /pet/{petId}
```

Update a pet’s basic attributes (`name`, `status`) via query parameters.

**Forwarding rules**

- Method: `POST`
- Upstream URL: `https://petstore3.swagger.io/api/v3/pet/{petId}`
- Path parameter forwarded.
- Query params:
  - `name` (optional)
  - `status` (optional)
- Headers: forward `Accept`, `Authorization`.
- Body: none (all fields in query).

#### Path parameters

| Name  | In   | Type  | Required | Description                    |
|-------|------|-------|----------|--------------------------------|
| petId | path | int64 | yes      | ID of pet that needs update   |

#### Query parameters

| Name   | In    | Type   | Required | Description                          |
|--------|-------|--------|----------|--------------------------------------|
| name   | query | string | no       | New pet name                         |
| status | query | string | no       | New pet status (`available`, etc.)   |

#### Success responses

| HTTP | Condition         | Body schema |
|------|-------------------|-------------|
| 200  | Pet updated       | `Pet`       |

#### Error responses

| HTTP | Condition         |
|------|-------------------|
| 400  | Invalid input     |
| 5xx  | Unexpected error  |

#### Example – cURL

```bash
curl -X POST "http://localhost:8080/api1/pet/10?name=doggie+updated&status=sold" \
  -H "Accept: application/json"
```

---

### Delete Pet

```
DELETE /pet/{petId}
```

Delete a pet from the store.

**Forwarding rules**

- Method: `DELETE`
- Upstream URL: `https://petstore3.swagger.io/api/v3/pet/{petId}`
- Path parameter forwarded.
- Header `api_key` forwarded if set.

#### Path parameters

| Name  | In   | Type  | Required | Description         |
|-------|------|-------|----------|---------------------|
| petId | path | int64 | yes      | Pet id to delete    |

#### Headers

| Name    | In     | Type   | Required | Description                           |
|---------|--------|--------|----------|---------------------------------------|
| api_key | header | string | no       | API key for authorization (optional) |

#### Success responses

| HTTP | Condition       | Body |
|------|-----------------|------|
| 200  | Pet deleted     | none |

#### Error responses

| HTTP | Condition             |
|------|-----------------------|
| 400  | Invalid pet value     |
| 5xx  | Unexpected error      |

#### Example – cURL

```bash
curl -X DELETE "http://localhost:8080/api1/pet/10" \
  -H "api_key: YOUR_API_KEY"
```

---

### Upload Pet Image

```
POST /pet/{petId}/uploadImage
```

Upload an image file for a pet.

**Forwarding rules**

- Method: `POST`
- Upstream URL: `https://petstore3.swagger.io/api/v3/pet/{petId}/uploadImage`
- Path parameter forwarded.
- Query param:
  - `additionalMetadata` (optional)
- Request body: binary (`application/octet-stream`) forwarded as-is.
- Headers: `Content-Type: application/octet-stream` preferred; SDK may convert from multipart (inferred).

#### Path parameters

| Name  | In   | Type  | Required | Description           |
|-------|------|-------|----------|-----------------------|
| petId | path | int64 | yes      | ID of pet to update   |

#### Query parameters

| Name               | In    | Type   | Required | Description         |
|--------------------|-------|--------|----------|---------------------|
| additionalMetadata | query | string | no       | Additional metadata |

#### Success responses

| HTTP | Condition         | Body schema  |
|------|-------------------|--------------|
| 200  | Upload succeeded  | `ApiResponse`|

`ApiResponse` example:

```json
{
  "code": 200,
  "type": "success",
  "message": "File uploaded"
}
```

#### Error responses

| HTTP | Condition         |
|------|-------------------|
| 400  | No file uploaded  |
| 404  | Pet not found     |
| 5xx  | Unexpected error  |

#### Example – cURL

```bash
# Example using raw binary (SDK will typically handle file reading)
curl -X POST "http://localhost:8080/api1/pet/10/uploadImage?additionalMetadata=profile" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@dog-photo.jpg"
```

---

### Get Inventory

```
GET /store/inventory
```

Return a map of pet status to inventory counts.

**Forwarding rules**

- Method: `GET`
- Upstream URL: `https://petstore3.swagger.io/api/v3/store/inventory`
- Headers:
  - Forward `Accept`, `api_key`, `Authorization`.

#### Path parameters

None.

#### Success responses

| HTTP | Condition         | Body schema                     |
|------|-------------------|----------------------------------|
| 200  | Inventory returned| `object<string, int32>` map      |

Example:

```json
{
  "available": 25,
  "pending": 3,
  "sold": 12
}
```

#### Error responses

| HTTP | Condition        |
|------|------------------|
| 5xx  | Unexpected error |

#### Example – cURL

```bash
curl -X GET "http://localhost:8080/api1/store/inventory" \
  -H "Accept: application/json" \
  -H "api_key: YOUR_API_KEY"
```

---

### Place Order

```
POST /store/order
```

Place a new order for a pet.

**Forwarding rules**

- Method: `POST`
- Upstream URL: `https://petstore3.swagger.io/api/v3/store/order`
- Body: `Order` JSON/XML/form forwarded as-is.

#### Path parameters

None.

#### Request body

`Order` object.

Example:

```json
{
  "id": 10,
  "petId": 198772,
  "quantity": 2,
  "shipDate": "2026-03-11T10:00:00Z",
  "status": "approved",
  "complete": true
}
```

#### Success responses

| HTTP | Condition           | Body schema |
|------|---------------------|-------------|
| 200  | Order placed        | `Order`     |

#### Error responses

| HTTP | Condition              |
|------|------------------------|
| 400  | Invalid input          |
| 422  | Validation exception   |
| 5xx  | Unexpected error       |

#### Example – cURL

```bash
curl -X POST "http://localhost:8080/api1/store/order" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "id": 10,
    "petId": 198772,
    "quantity": 2,
    "shipDate": "2026-03-11T10:00:00Z",
    "status": "approved",
    "complete": true
  }'
```

---

### Get Order by ID

```
GET /store/order/{orderId}
```

Retrieve an order by its ID. For valid responses, use IDs `<= 5` or `> 10` (per upstream description).

**Forwarding rules**

- Method: `GET`
- Upstream URL: `https://petstore3.swagger.io/api/v3/store/order/{orderId}`

#### Path parameters

| Name    | In   | Type  | Required | Description                       |
|---------|------|-------|----------|-----------------------------------|
| orderId | path | int64 | yes      | ID of order that needs to be fetched |

#### Success responses

| HTTP | Condition        | Body schema |
|------|------------------|-------------|
| 200  | Order found      | `Order`     |

#### Error responses

| HTTP | Condition             |
|------|-----------------------|
| 400  | Invalid ID supplied   |
| 404  | Order not found       |
| 5xx  | Unexpected error      |

#### Example – cURL

```bash
curl -X GET "http://localhost:8080/api1/store/order/10" \
  -H "Accept: application/json"
```

#### Example response

```json
{
  "id": 10,
  "petId": 198772,
  "quantity": 2,
  "shipDate": "2026-03-11T10:00:00Z",
  "status": "approved",
  "complete": true
}
```

---

### Delete Order

```
DELETE /store/order/{orderId}
```

Delete an order by ID. For valid delete responses, use IDs `< 1000` (per upstream description).

**Forwarding rules**

- Method: `DELETE`
- Upstream URL: `https://petstore3.swagger.io/api/v3/store/order/{orderId}`

#### Path parameters

| Name    | In   | Type  | Required | Description                              |
|---------|------|-------|----------|------------------------------------------|
| orderId | path | int64 | yes      | ID of the order that needs to be deleted |

#### Success responses

| HTTP | Condition        | Body |
|------|------------------|------|
| 200  | Order deleted    | none |

#### Error responses

| HTTP | Condition             |
|------|-----------------------|
| 400  | Invalid ID supplied   |
| 404  | Order not found       |
| 5xx  | Unexpected error      |

#### Example – cURL

```bash
curl -X DELETE "http://localhost:8080/api1/store/order/10"
```

---

### Create User

```
POST /user
```

Create a single user.

**Forwarding rules**

- Method: `POST`
- Upstream URL: `https://petstore3.swagger.io/api/v3/user`

#### Request body

`User` object.

Example:

```json
{
  "id": 10,
  "username": "theUser",
  "firstName": "John",
  "lastName": "James",
  "email": "john@email.com",
  "password": "12345",
  "phone": "12345",
  "userStatus": 1
}
```

#### Success responses

| HTTP | Condition          | Body schema |
|------|--------------------|-------------|
| 200  | User created       | `User`      |

#### Error responses

| HTTP | Condition        |
|------|------------------|
| 5xx  | Unexpected error |

#### Example – cURL

```bash
curl -X POST "http://localhost:8080/api1/user" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "id": 10,
    "username": "theUser",
    "firstName": "John",
    "lastName": "James",
    "email": "john@email.com",
    "password": "12345",
    "phone": "12345",
    "userStatus": 1
  }'
```

---

### Create Users with List Input

```
POST /user/createWithList
```

Create multiple users in a single request.

**Forwarding rules**

- Method: `POST`
- Upstream URL: `https://petstore3.swagger.io/api/v3/user/createWithList`

#### Request body

Array of `User` objects.

Example:

```json
[
  {
    "id": 11,
    "username": "user1",
    "firstName": "Alice",
    "lastName": "Smith",
    "email": "alice@example.com",
    "password": "pwd1",
    "phone": "111-111-1111",
    "userStatus": 1
  },
  {
    "id": 12,
    "username": "user2",
    "firstName": "Bob",
    "lastName": "Jones",
    "email": "bob@example.com",
    "password": "pwd2",
    "phone": "222-222-2222",
    "userStatus": 1
  }
]
```

#### Success responses

| HTTP | Condition            | Body schema |
|------|----------------------|-------------|
| 200  | Users created        | `User`      |

(Upstream returns a `User` object, likely a status user representation.)

#### Error responses

| HTTP | Condition        |
|------|------------------|
| 5xx  | Unexpected error |

#### Example – cURL

```bash
curl -X POST "http://localhost:8080/api1/user/createWithList" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '[{
    "id": 11,
    "username": "user1",
    "firstName": "Alice",
    "lastName": "Smith",
    "email": "alice@example.com",
    "password": "pwd1",
    "phone": "111-111-1111",
    "userStatus": 1
  }]'
```

---

### Login User

```
GET /user/login
```

Log a user into the system. Returns a session token string (semantics defined by upstream).

**Forwarding rules**

- Method: `GET`
- Upstream URL: `https://petstore3.swagger.io/api/v3/user/login`
- Query params: `username`, `password`.

#### Query parameters

| Name     | In    | Type   | Required | Description                       |
|----------|-------|--------|----------|-----------------------------------|
| username | query | string | no       | The user name for login           |
| password | query | string | no       | Clear-text password               |

#### Success responses

| HTTP | Condition            | Body schema | Headers                                           |
|------|----------------------|-------------|---------------------------------------------------|
| 200  | Login successful     | `string`    | `X-Rate-Limit`, `X-Expires-After` (date-time)     |

Example body:

```text
"logged in user session: 123456789"
```

#### Error responses

| HTTP | Condition                          |
|------|------------------------------------|
| 400  | Invalid username/password supplied |
| 5xx  | Unexpected error                   |

#### Example – cURL

```bash
curl -X GET "http://localhost:8080/api1/user/login?username=theUser&password=12345" \
  -H "Accept: application/json"
```

---

### Logout User

```
GET /user/logout
```

Log out the current logged-in user session.

**Forwarding rules**

- Method: `GET`
- Upstream URL: `https://petstore3.swagger.io/api/v3/user/logout`

#### Success responses

| HTTP | Condition           |
|------|---------------------|
| 200  | Logout successful   |

#### Error responses

| HTTP | Condition        |
|------|------------------|
| 5xx  | Unexpected error |

#### Example – cURL

```bash
curl -X GET "http://localhost:8080/api1/user/logout"
```

---

### Get User by Username

```
GET /user/{username}
```

Retrieve details for a given username.

**Forwarding rules**

- Method: `GET`
- Upstream URL: `https://petstore3.swagger.io/api/v3/user/{username}`

#### Path parameters

| Name     | In   | Type   | Required | Description                                    |
|----------|------|--------|----------|------------------------------------------------|
| username | path | string | yes      | The name that needs to be fetched (e.g. user1) |

#### Success responses

| HTTP | Condition      | Body schema |
|------|----------------|-------------|
| 200  | User found     | `User`      |

#### Error responses

| HTTP | Condition                  |
|------|----------------------------|
| 400  | Invalid username supplied  |
| 404  | User not found             |
| 5xx  | Unexpected error           |

#### Example – cURL

```bash
curl -X GET "http://localhost:8080/api1/user/user1" \
  -H "Accept: application/json"
```

#### Example response

```json
{
  "id": 21,
  "username": "user1",
  "firstName": "Test",
  "lastName": "User",
  "email": "user1@example.com",
  "password": "*****",
  "phone": "555-000-0001",
  "userStatus": 1
}
```

---

### Update User

```
PUT /user/{username}
```

Update an existing user’s data.

**Forwarding rules**

- Method: `PUT`
- Upstream URL: `https://petstore3.swagger.io/api/v3/user/{username}`

#### Path parameters

| Name     | In   | Type   | Required | Description                     |
|----------|------|--------|----------|---------------------------------|
| username | path | string | yes      | Name of the user to be updated |

#### Request body

`User` object with updated fields.

Example:

```json
{
  "id": 21,
  "username": "user1",
  "firstName": "TestUpdated",
  "lastName": "User",
  "email": "user1_updated@example.com",
  "password": "newpwd",
  "phone": "555-000-0001",
  "userStatus": 1
}
```

#### Success responses

| HTTP | Condition         |
|------|-------------------|
| 200  | User updated      |

#### Error responses

| HTTP | Condition      |
|------|----------------|
| 400  | bad request    |
| 404  | user not found |
| 5xx  | Unexpected     |

#### Example – cURL

```bash
curl -X PUT "http://localhost:8080/api1/user/user1" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 21,
    "username": "user1",
    "firstName": "TestUpdated",
    "lastName": "User",
    "email": "user1_updated@example.com",
    "password": "newpwd",
    "phone": "555-000-0001",
    "userStatus": 1
  }'
```

---

### Delete User

```
DELETE /user/{username}
```

Delete a user by username.

**Forwarding rules**

- Method: `DELETE`
- Upstream URL: `https://petstore3.swagger.io/api/v3/user/{username}`

#### Path parameters

| Name     | In   | Type   | Required | Description                         |
|----------|------|--------|----------|-------------------------------------|
| username | path | string | yes      | The name of the user to be deleted |

#### Success responses

| HTTP | Condition       |
|------|-----------------|
| 200  | User deleted    |

#### Error responses

| HTTP | Condition                  |
|------|----------------------------|
| 400  | Invalid username supplied  |
| 404  | User not found             |
| 5xx  | Unexpected error           |

#### Example – cURL

```bash
curl -X DELETE "http://localhost:8080/api1/user/user1"
```

---

## Orchestrator API Contract

No additional backend orchestrator is defined beyond the upstream Petstore API itself. All SDK proxy operations are direct pass-throughs to the Petstore endpoints described above (no extra orchestration endpoints are specified).

---

## Mock Destination API Contract

No dedicated mock/demo services are defined in the provided specification.  
For testing, the SDK proxy can be configured (inferred) to point to a mock base URL instead of the real Petstore:

- **Mock upstream (inferred)**: `http://localhost:9090/mock-petstore`

Expected behavior for mocks (inferred):

- Same paths, methods, and schemas as the real Petstore:
  - `/pet`, `/pet/{petId}`, `/store/order`, `/user/{username}`, etc.
- Responses:
  - Deterministic canned responses based on IDs (e.g. `petId=10` returns a fixed `Pet` object).
  - Error codes `400`/`404` simulated for invalid IDs or usernames.
- Content types and security headers may be ignored by the mock unless explicitly configured.