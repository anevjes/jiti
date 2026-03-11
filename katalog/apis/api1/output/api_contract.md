# SDK Proxy API Contract

**Feature**: api1  
**Date**: 2026-03-11  
**Component**: /petstore/api1

---

## Base URL

SDK proxy runs in front of the Petstore API and simply forwards requests and responses.

- **Local (developer)**: `http://localhost:8080/api1`
- **Debug / Staging**: `https://dev-api.example.com/api1`

Upstream (destination) Petstore server (from Swagger):

- **Destination**: `https://petstore3.swagger.io/api/v3`

Unless otherwise noted, the SDK proxy:

- Preserves HTTP method, path, and query string.
- Forwards body as‑is.
- Forwards all non-hop-by-hop headers, plus any configured auth headers.
- Streams response status, headers, and body back unchanged.

---

## Endpoints

### Add Pet

```
POST /pet
```

Create a new pet in the store.

**Destination mapping**

- Forward to: `POST https://petstore3.swagger.io/api/v3/pet`
- Proxy path: `/api1/pet` → destination `/pet`

#### Request

- **Body (required)**: `Pet` (JSON/XML/form)
- Supported content types:
  - `application/json`
  - `application/xml`
  - `application/x-www-form-urlencoded`
- Auth:
  - OAuth2 `petstore_auth` with scopes `write:pets`, `read:pets` (inferred: SDK should accept an access token and pass as `Authorization: Bearer <token>`)

**Pet schema**

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
    { "id": 100, "name": "friendly" }
  ],
  "status": "available"
}
```

#### Response forwarding rules

- Forward upstream status code and body unchanged.
- For `200`, parse as `Pet` for strongly typed SDKs; otherwise treat as opaque JSON/XML.
- For `400`, `422`, and default, treat as error; expose status and raw body.

#### Success responses

| HTTP | Description             | Body type |
|------|-------------------------|-----------|
| 200  | Successful operation    | `Pet`     |

#### Error responses

| HTTP | Description           | Body type  |
|------|-----------------------|-----------|
| 400  | Invalid input         | none      |
| 422  | Validation exception  | none      |
| 5xx* | Unexpected error      | none/text |

#### Example – curl

```bash
curl -X POST "http://localhost:8080/api1/pet" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 10,
    "name": "doggie",
    "category": { "id": 1, "name": "Dogs" },
    "photoUrls": ["https://example.com/photos/dog1.jpg"],
    "tags": [{ "id": 100, "name": "friendly" }],
    "status": "available"
  }'
```

**Upstream HTTP request**

```http
POST /api/v3/pet HTTP/1.1
Host: petstore3.swagger.io
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
Content-Length: 207

{ ...Pet JSON as above... }
```

**Upstream HTTP response**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 10,
  "name": "doggie",
  "category": { "id": 1, "name": "Dogs" },
  "photoUrls": ["https://example.com/photos/dog1.jpg"],
  "tags": [{ "id": 100, "name": "friendly" }],
  "status": "available"
}
```

---

### Update Pet

```
PUT /pet
```

Update an existing pet by Id.

**Destination mapping**

- Forward to: `PUT https://petstore3.swagger.io/api/v3/pet`

#### Request

- **Body (required)**: `Pet` object (includes `id` of existing pet).
- Content types: `application/json`, `application/xml`, `application/x-www-form-urlencoded`.
- Auth: `petstore_auth` with `write:pets`, `read:pets`.

#### Response forwarding rules

Same as **Add Pet**.

#### Success responses

| HTTP | Description          | Body type |
|------|----------------------|-----------|
| 200  | Successful operation | `Pet`     |

#### Error responses

| HTTP | Description            |
|------|------------------------|
| 400  | Invalid ID supplied    |
| 404  | Pet not found          |
| 422  | Validation exception   |
| 5xx* | Unexpected error       |

#### Example – curl

```bash
curl -X PUT "http://localhost:8080/api1/pet" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 10,
    "name": "doggie-2",
    "category": { "id": 1, "name": "Dogs" },
    "photoUrls": ["https://example.com/photos/dog1.jpg"],
    "tags": [{ "id": 100, "name": "friendly" }],
    "status": "pending"
  }'
```

---

### Find Pets by Status

```
GET /pet/findByStatus
```

Find pets filtered by status. Multiple status values can be provided via comma-separated strings (per upstream description).

**Destination mapping**

- Forward to: `GET https://petstore3.swagger.io/api/v3/pet/findByStatus`

#### Path & query parameters

| Name   | In    | Type   | Required | Description                                               |
|--------|-------|--------|----------|-----------------------------------------------------------|
| status | query | string | yes      | `available`, `pending`, or `sold` (comma-separated list) |

#### Response forwarding rules

- For `200`, forward list of `Pet` objects.
- For `400` or default, propagate as error.

#### Success responses

| HTTP | Description           | Body type  |
|------|-----------------------|------------|
| 200  | successful operation  | `Pet[]`    |

#### Error responses

| HTTP | Description           |
|------|-----------------------|
| 400  | Invalid status value  |
| 5xx* | Unexpected error      |

#### Example – curl

```bash
curl -X GET "http://localhost:8080/api1/pet/findByStatus?status=available,pending" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Sample 200 response**

```json
[
  {
    "id": 10,
    "name": "doggie",
    "category": { "id": 1, "name": "Dogs" },
    "photoUrls": ["https://example.com/photos/dog1.jpg"],
    "tags": [{ "id": 100, "name": "friendly" }],
    "status": "available"
  },
  {
    "id": 11,
    "name": "mittens",
    "category": { "id": 2, "name": "Cats" },
    "photoUrls": ["https://example.com/photos/cat1.jpg"],
    "tags": [{ "id": 101, "name": "indoor" }],
    "status": "pending"
  }
]
```

---

### Find Pets by Tags

```
GET /pet/findByTags
```

Find pets by tags. Multiple tags can be provided with comma-separated strings.

**Destination mapping**

- Forward to: `GET https://petstore3.swagger.io/api/v3/pet/findByTags`

#### Query parameters

| Name | In    | Type        | Required | Description      |
|------|-------|-------------|----------|------------------|
| tags | query | string\[]   | yes      | Tags to filter by |

SDK should allow array input and format as `?tags=tag1,tag2`.

#### Response & error handling

Same structure as **Find Pets by Status**, but for tag filtering.

#### Example – curl

```bash
curl -X GET "http://localhost:8080/api1/pet/findByTags?tags=tag1,tag2" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Sample 200 response**

```json
[
  {
    "id": 15,
    "name": "parrot",
    "category": { "id": 3, "name": "Birds" },
    "photoUrls": ["https://example.com/photos/parrot1.jpg"],
    "tags": [{ "id": 200, "name": "tag1" }],
    "status": "available"
  }
]
```

---

### Get Pet by ID

```
GET /pet/{petId}
```

Retrieve details of a single pet by ID.

**Destination mapping**

- Forward to: `GET https://petstore3.swagger.io/api/v3/pet/{petId}`

#### Path parameters

| Name  | In   | Type    | Required | Description          |
|-------|------|---------|----------|----------------------|
| petId | path | int64   | yes      | ID of pet to return  |

#### Auth

- Either:
  - API key: header `api_key: <KEY>`, or
  - OAuth2 `petstore_auth` with `write:pets`, `read:pets`.

SDK should expose both options.

#### Success responses

| HTTP | Description           | Body type |
|------|-----------------------|-----------|
| 200  | successful operation  | `Pet`     |

#### Error responses

| HTTP | Description          |
|------|----------------------|
| 400  | Invalid ID supplied  |
| 404  | Pet not found        |
| 5xx* | Unexpected error     |

#### Example – curl

```bash
curl -X GET "http://localhost:8080/api1/pet/10" \
  -H "api_key: <API_KEY>"
```

**Sample 200 response**

```json
{
  "id": 10,
  "name": "doggie",
  "category": { "id": 1, "name": "Dogs" },
  "photoUrls": ["https://example.com/photos/dog1.jpg"],
  "tags": [{ "id": 100, "name": "friendly" }],
  "status": "available"
}
```

---

### Update Pet with Form

```
POST /pet/{petId}
```

Update a pet’s basic fields using form-like parameters (here expressed as query parameters per spec).

**Destination mapping**

- Forward to: `POST https://petstore3.swagger.io/api/v3/pet/{petId}`

#### Path & query parameters

| Name  | In    | Type   | Required | Description                                |
|-------|-------|--------|----------|--------------------------------------------|
| petId | path  | int64  | yes      | ID of pet that needs to be updated         |
| name  | query | string | no       | Name of pet that needs to be updated       |
| status| query | string | no       | Status of pet that needs to be updated     |

#### Success responses

| HTTP | Description           | Body type |
|------|-----------------------|-----------|
| 200  | successful operation  | `Pet`     |

#### Error responses

| HTTP | Description   |
|------|---------------|
| 400  | Invalid input |
| 5xx* | Unexpected    |

#### Example – curl

```bash
curl -X POST "http://localhost:8080/api1/pet/10?name=doggie-updated&status=sold" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

### Delete Pet

```
DELETE /pet/{petId}
```

Delete a pet by ID.

**Destination mapping**

- Forward to: `DELETE https://petstore3.swagger.io/api/v3/pet/{petId}`

#### Path & header parameters

| Name   | In     | Type   | Required | Description          |
|--------|--------|--------|----------|----------------------|
| petId  | path   | int64  | yes      | Pet id to delete     |
| api_key| header | string | no       | Optional API key     |

#### Success responses

| HTTP | Description   |
|------|---------------|
| 200  | Pet deleted   |

#### Error responses

| HTTP | Description         |
|------|---------------------|
| 400  | Invalid pet value   |
| 5xx* | Unexpected error    |

#### Example – curl

```bash
curl -X DELETE "http://localhost:8080/api1/pet/10" \
  -H "api_key: <API_KEY>"
```

---

### Upload Pet Image

```
POST /pet/{petId}/uploadImage
```

Upload an image for a pet.

**Destination mapping**

- Forward to: `POST https://petstore3.swagger.io/api/v3/pet/{petId}/uploadImage`

#### Parameters

| Name              | In    | Type   | Required | Description         |
|-------------------|-------|--------|----------|---------------------|
| petId             | path  | int64  | yes      | ID of pet to update |
| additionalMetadata| query | string | no       | Additional metadata |

#### Request body

- Content type: `application/octet-stream`
- Body: binary file stream (image data).

#### Success responses

| HTTP | Description           | Body type     |
|------|-----------------------|---------------|
| 200  | successful operation  | `ApiResponse` |

`ApiResponse` schema:

```json
{
  "code": 200,
  "type": "success",
  "message": "File uploaded"
}
```

#### Error responses

| HTTP | Description       |
|------|-------------------|
| 400  | No file uploaded  |
| 404  | Pet not found     |
| 5xx* | Unexpected error  |

#### Example – curl

```bash
curl -X POST "http://localhost:8080/api1/pet/10/uploadImage?additionalMetadata=profile" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@./dog.jpg"
```

---

### Get Inventory

```
GET /store/inventory
```

Returns pet inventories by status as a simple map of status → quantity.

**Destination mapping**

- Forward to: `GET https://petstore3.swagger.io/api/v3/store/inventory`

#### Auth

- Requires API key: `api_key` header.

#### Success responses

| HTTP | Description           | Body type             |
|------|-----------------------|-----------------------|
| 200  | successful operation  | `object<string,int>` |

Example:

```json
{
  "available": 15,
  "pending": 3,
  "sold": 27
}
```

#### Error responses

| HTTP | Description      |
|------|------------------|
| 5xx* | Unexpected error |

#### Example – curl

```bash
curl -X GET "http://localhost:8080/api1/store/inventory" \
  -H "api_key: <API_KEY>"
```

---

### Place Order

```
POST /store/order
```

Place an order for a pet.

**Destination mapping**

- Forward to: `POST https://petstore3.swagger.io/api/v3/store/order`

#### Request body

- Content types: `application/json`, `application/xml`, `application/x-www-form-urlencoded`
- Body: `Order`

`Order` schema:

```json
{
  "id": 10,
  "petId": 198772,
  "quantity": 7,
  "shipDate": "2026-03-11T10:15:30Z",
  "status": "approved",
  "complete": true
}
```

#### Success responses

| HTTP | Description           | Body type |
|------|-----------------------|-----------|
| 200  | successful operation  | `Order`   |

#### Error responses

| HTTP | Description           |
|------|-----------------------|
| 400  | Invalid input         |
| 422  | Validation exception  |
| 5xx* | Unexpected error      |

#### Example – curl

```bash
curl -X POST "http://localhost:8080/api1/store/order" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 10,
    "petId": 198772,
    "quantity": 1,
    "shipDate": "2026-03-11T10:15:30Z",
    "status": "placed",
    "complete": false
  }'
```

---

### Get Order by ID

```
GET /store/order/{orderId}
```

Find purchase order by ID.

**Destination mapping**

- Forward to: `GET https://petstore3.swagger.io/api/v3/store/order/{orderId}`

#### Path parameters

| Name    | In   | Type  | Required | Description                                                       |
|---------|------|-------|----------|-------------------------------------------------------------------|
| orderId | path | int64 | yes      | ID of order that needs to be fetched                              |

Note from API: valid responses for IDs ≤ 5 or > 10; others generate exceptions.

#### Success responses

| HTTP | Description           | Body type |
|------|-----------------------|-----------|
| 200  | successful operation  | `Order`   |

#### Error responses

| HTTP | Description           |
|------|-----------------------|
| 400  | Invalid ID supplied   |
| 404  | Order not found       |
| 5xx* | Unexpected error      |

#### Example – curl

```bash
curl -X GET "http://localhost:8080/api1/store/order/10"
```

**Sample 200 response**

```json
{
  "id": 10,
  "petId": 198772,
  "quantity": 1,
  "shipDate": "2026-03-11T10:15:30Z",
  "status": "approved",
  "complete": true
}
```

---

### Delete Order

```
DELETE /store/order/{orderId}
```

Delete purchase order by ID.

**Destination mapping**

- Forward to: `DELETE https://petstore3.swagger.io/api/v3/store/order/{orderId}`

#### Path parameters

| Name    | In   | Type  | Required | Description                                                       |
|---------|------|-------|----------|-------------------------------------------------------------------|
| orderId | path | int64 | yes      | ID of the order that needs to be deleted                          |

Valid only for `orderId < 1000` (per description).

#### Success responses

| HTTP | Description  |
|------|--------------|
| 200  | order deleted|

#### Error responses

| HTTP | Description           |
|------|-----------------------|
| 400  | Invalid ID supplied   |
| 404  | Order not found       |
| 5xx* | Unexpected error      |

#### Example – curl

```bash
curl -X DELETE "http://localhost:8080/api1/store/order/10"
```

---

### Create User

```
POST /user
```

Create a single user. Intended for logged-in administrators or self-registration flows.

**Destination mapping**

- Forward to: `POST https://petstore3.swagger.io/api/v3/user`

#### Request body

- Content types: `application/json`, `application/xml`, `application/x-www-form-urlencoded`
- Body: `User`

`User` schema:

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

| HTTP | Description           | Body type |
|------|-----------------------|-----------|
| 200  | successful operation  | `User`    |

#### Error responses

| HTTP | Description      |
|------|------------------|
| 5xx* | Unexpected error |

#### Example – curl

```bash
curl -X POST "http://localhost:8080/api1/user" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "firstName": "Alice",
    "lastName": "Anderson",
    "email": "alice@example.com",
    "password": "secret",
    "phone": "+123456789",
    "userStatus": 1
  }'
```

---

### Create Users with List Input

```
POST /user/createWithList
```

Bulk create users from an array.

**Destination mapping**

- Forward to: `POST https://petstore3.swagger.io/api/v3/user/createWithList`

#### Request body

- Content type: `application/json`
- Body: `User[]`

Example:

```json
[
  {
    "username": "user1",
    "firstName": "User",
    "lastName": "One",
    "email": "user1@example.com",
    "password": "pass1",
    "phone": "111111111",
    "userStatus": 1
  },
  {
    "username": "user2",
    "firstName": "User",
    "lastName": "Two",
    "email": "user2@example.com",
    "password": "pass2",
    "phone": "222222222",
    "userStatus": 1
  }
]
```

#### Success responses

| HTTP | Description           | Body type |
|------|-----------------------|-----------|
| 200  | Successful operation  | `User`    |

#### Error responses

| HTTP | Description      |
|------|------------------|
| 5xx* | Unexpected error |

#### Example – curl

```bash
curl -X POST "http://localhost:8080/api1/user/createWithList" \
  -H "Content-Type: application/json" \
  -d '[{ "username": "user1" }, { "username": "user2" }]'
```

---

### Login User

```
GET /user/login
```

Log a user into the system.

**Destination mapping**

- Forward to: `GET https://petstore3.swagger.io/api/v3/user/login`

#### Query parameters

| Name     | In    | Type   | Required | Description                         |
|----------|-------|--------|----------|-------------------------------------|
| username | query | string | no       | The user name for login             |
| password | query | string | no       | The password for login in cleartext |

#### Success responses

| HTTP | Description           | Body type | Headers                                      |
|------|-----------------------|-----------|----------------------------------------------|
| 200  | successful operation  | string    | `X-Rate-Limit`, `X-Expires-After`            |

Example headers:

```http
X-Rate-Limit: 1000
X-Expires-After: 2026-03-11T11:15:30Z
```

Body example:

```json
"logged in user session: 1234567890"
```

#### Error responses

| HTTP | Description                         |
|------|-------------------------------------|
| 400  | Invalid username/password supplied  |
| 5xx* | Unexpected error                    |

#### Example – curl

```bash
curl -X GET "http://localhost:8080/api1/user/login?username=alice&password=secret"
```

---

### Logout User

```
GET /user/logout
```

Log out the current user.

**Destination mapping**

- Forward to: `GET https://petstore3.swagger.io/api/v3/user/logout`

#### Success responses

| HTTP | Description           |
|------|-----------------------|
| 200  | successful operation  |

#### Error responses

| HTTP | Description      |
|------|------------------|
| 5xx* | Unexpected error |

#### Example – curl

```bash
curl -X GET "http://localhost:8080/api1/user/logout"
```

---

### Get User by Username

```
GET /user/{username}
```

Retrieve user details by username.

**Destination mapping**

- Forward to: `GET https://petstore3.swagger.io/api/v3/user/{username}`

#### Path parameters

| Name     | In   | Type   | Required | Description                            |
|----------|------|--------|----------|----------------------------------------|
| username | path | string | yes      | Name that needs to be fetched          |

#### Success responses

| HTTP | Description           | Body type |
|------|-----------------------|-----------|
| 200  | successful operation  | `User`    |

#### Error responses

| HTTP | Description                 |
|------|-----------------------------|
| 400  | Invalid username supplied   |
| 404  | User not found              |
| 5xx* | Unexpected error            |

#### Example – curl

```bash
curl -X GET "http://localhost:8080/api1/user/alice"
```

**Sample 200 response**

```json
{
  "id": 10,
  "username": "alice",
  "firstName": "Alice",
  "lastName": "Anderson",
  "email": "alice@example.com",
  "password": "****",
  "phone": "+123456789",
  "userStatus": 1
}
```

---

### Update User

```
PUT /user/{username}
```

Update an existing user.

**Destination mapping**

- Forward to: `PUT https://petstore3.swagger.io/api/v3/user/{username}`

#### Path parameters

| Name     | In   | Type   | Required | Description                      |
|----------|------|--------|----------|----------------------------------|
| username | path | string | yes      | Name of user to update           |

#### Request body

- Content types: `application/json`, `application/xml`, `application/x-www-form-urlencoded`
- Body: `User` (updated fields).

#### Success responses

| HTTP | Description           |
|------|-----------------------|
| 200  | successful operation  |

#### Error responses

| HTTP | Description      |
|------|------------------|
| 400  | bad request      |
| 404  | user not found   |
| 5xx* | Unexpected error |

#### Example – curl

```bash
curl -X PUT "http://localhost:8080/api1/user/alice" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "firstName": "Alice",
    "lastName": "A.",
    "email": "alice@example.com",
    "password": "new-secret",
    "phone": "+123456789",
    "userStatus": 1
  }'
```

---

### Delete User

```
DELETE /user/{username}
```

Delete a user by username.

**Destination mapping**

- Forward to: `DELETE https://petstore3.swagger.io/api/v3/user/{username}`

#### Path parameters

| Name     | In   | Type   | Required | Description                     |
|----------|------|--------|----------|---------------------------------|
| username | path | string | yes      | The name that needs to be deleted |

#### Success responses

| HTTP | Description   |
|------|---------------|
| 200  | User deleted  |

#### Error responses

| HTTP | Description                 |
|------|-----------------------------|
| 400  | Invalid username supplied   |
| 404  | User not found              |
| 5xx* | Unexpected error            |

#### Example – curl

```bash
curl -X DELETE "http://localhost:8080/api1/user/alice"
```

---

## Orchestrator API Contract

No separate backend orchestration layer is described. All SDK proxy calls are direct pass-through to the Petstore API:

- Base: `https://petstore3.swagger.io/api/v3`
- Paths and semantics as detailed above.
- Orchestration behaviors (e.g., fan-out, data aggregation) are **not** defined in the supplied Swagger and are therefore not implemented.

If an orchestrator is introduced later (e.g., combining pet + order data in one call), those endpoints will be additive and explicitly marked as “(inferred)” or “orchestrated” in a future revision.

---

## Mock Destination API Contract

No explicit mock/demo services are defined in the supplied documentation.

For local development it is reasonable to provide a mock Petstore service (inferred) behind the SDK proxy. Any such mock should:

- Listen on: `http://localhost:9090/api/v3` (inferred)
- Implement the same paths, methods, and schemas as the real Petstore server.
- Return deterministic stub data, e.g.:

### (inferred) Example Mock – Get Pet by ID

```
GET /pet/{petId}
```

**Sample mock response**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 10,
  "name": "mock-doggie",
  "category": { "id": 1, "name": "Dogs" },
  "photoUrls": ["https://mock/photos/dog1.jpg"],
  "tags": [{ "id": 1, "name": "mock" }],
  "status": "available"
}
```

The SDK proxy should be configurable to point either at the real Petstore base URL or at this mock base URL, while keeping the SDK surface identical.