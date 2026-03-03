# SDK Proxy API Contract

**Feature**: api1  
**Date**: 2026-03-03  
**Component**: /api/v3

## Base URL

Local: http://localhost:3000/api/v3  
Debug: http://localhost:3000/debug/api/v3

---

## Endpoints

### Update an existing pet

```
PUT /pet
```

Description: Updates an existing pet. Request body must be a full Pet object.

Path parameters: none.

Request forwarding rules:
- Proxy forwards the full request body as-is.
- Requires OAuth2 `petstore_auth` with scopes `write:pets` and `read:pets`.

Success responses:
- 200: Updated Pet object.

Error responses:
- 400: Invalid ID supplied
- 404: Pet not found
- 422: Validation exception
- default: Unexpected error

Example cURL:

```
curl -X PUT http://localhost:3000/api/v3/pet \
  -H "Content-Type: application/json" \
  -d '{"id":10,"name":"doggie","photoUrls":["url1"],"status":"available"}'
```

---

### Add a new pet

```
POST /pet
```

Description: Creates a new pet in the store.

Path parameters: none.

Request forwarding rules:
- Body is forwarded intact.

Success responses:
- 200: Created Pet object.

Error responses:
- 400: Invalid input
- 422: Validation exception
- default: Unexpected error

Example cURL:

```
curl -X POST http://localhost:3000/api/v3/pet \
  -H "Content-Type: application/json" \
  -d '{"name":"doggie","photoUrls":["url1"]}'
```

---

### Find pets by status

```
GET /pet/findByStatus
```

Description: Returns pets filtered by status.

Path parameters: none.

Query parameters:
- status (required) string enum: available, pending, sold

Success:
- 200: Array of Pet

Errors:
- 400: Invalid status value
- default: Unexpected error

Example:

```
curl "http://localhost:3000/api/v3/pet/findByStatus?status=available"
```

---

### Find pets by tags

```
GET /pet/findByTags
```

Description: Returns pets matching supplied tags.

Query parameters:
- tags (required) array of strings

Success:
- 200: Array of Pet

Errors:
- 400: Invalid tag value
- default: Unexpected error

Example:

```
curl "http://localhost:3000/api/v3/pet/findByTags?tags=tag1&tags=tag2"
```

---

### Get pet by ID

```
GET /pet/{petId}
```

Description: Retrieve a single pet.

Path parameters:
- petId (required) int64

Success:
- 200: Pet

Errors:
- 400: Invalid ID supplied
- 404: Pet not found
- default: Unexpected error

Example:

```
curl http://localhost:3000/api/v3/pet/10
```

---

### Update pet using form data

```
POST /pet/{petId}
```

Description: Partial update of a pet using form-like query parameters.

Path parameters:
- petId (required)

Query parameters:
- name
- status

Success:
- 200: Pet

Errors:
- 400: Invalid input
- default: Unexpected error

Example:

```
curl -X POST "http://localhost:3000/api/v3/pet/10?name=newname&status=sold"
```

---

### Delete pet

```
DELETE /pet/{petId}
```

Description: Delete pet by ID.

Path parameters:
- petId (required)

Headers:
- api_key (optional)

Success:
- 200: Pet deleted

Errors:
- 400: Invalid pet value
- default: Unexpected error

Example:

```
curl -X DELETE http://localhost:3000/api/v3/pet/10
```

---

### Upload pet image

```
POST /pet/{petId}/uploadImage
```

Description: Uploads an image file for a pet.

Path parameters:
- petId (required)

Query:
- additionalMetadata (optional)

Body:
- binary file sent as application/octet-stream

Success:
- 200: ApiResponse

Errors:
- 400: No file uploaded
- 404: Pet not found
- default: Unexpected error

Example:

```
curl -X POST http://localhost:3000/api/v3/pet/10/uploadImage \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@photo.png"
```

---

### Get store inventory

```
GET /store/inventory
```

Description: Returns inventory counts by status.

Success:
- 200: object with key=status, value=quantity

Errors:
- default: Unexpected error

Example:
```
curl http://localhost:3000/api/v3/store/inventory
```

---

### Place an order

```
POST /store/order
```

Description: Places a new order.

Body: Order object

Success:
- 200: Order

Errors:
- 400: Invalid input
- 422: Validation exception
- default: Unexpected error

Example:
```
curl -X POST http://localhost:3000/api/v3/store/order \
  -H "Content-Type: application/json" \
  -d '{"petId":198772,"quantity":7}'
```

---

### Get order by ID

```
GET /store/order/{orderId}
```

Description: Fetch order by ID. Valid IDs: <=5 or >10.

Path parameters:
- orderId (required)

Success:
- 200: Order

Errors:
- 400: Invalid ID supplied
- 404: Order not found
- default: Unexpected error

Example:
```
curl http://localhost:3000/api/v3/store/order/5
```

---

### Delete order by ID

```
DELETE /store/order/{orderId}
```

Description: Delete order. Valid IDs <1000.

Path:
- orderId

Success:
- 200: order deleted

Errors:
- 400: Invalid ID supplied
- 404: Order not found
- default: Unexpected error

Example:
```
curl -X DELETE http://localhost:3000/api/v3/store/order/20
```

---

### Create user

```
POST /user
```

Description: Create a user.

Body: User object

Success:
- 200: User

Errors:
- default: Unexpected error

Example:
```
curl -X POST http://localhost:3000/api/v3/user \
  -H "Content-Type: application/json" \
  -d '{"username":"theUser"}'
```

---

### Create users with list

```
POST /user/createWithList
```

Description: Create users in bulk.

Body: array of User

Success:
- 200: User

Errors:
- default: Unexpected error

Example:
```
curl -X POST http://localhost:3000/api/v3/user/createWithList \
  -H "Content-Type: application/json" \
  -d '[{"username":"user1"}]'
```

---

### Login user

```
GET /user/login
```

Description: Login with username/password.

Query:
- username
- password

Success:
- 200: string token

Errors:
- 400: Invalid username/password
- default: Unexpected error

Example:
```
curl "http://localhost:3000/api/v3/user/login?username=user&password=pw"
```

---

### Logout user

```
GET /user/logout
```

Description: Logs out current session.

Success:
- 200

Errors:
- default

Example:
```
curl http://localhost:3000/api/v3/user/logout
```

---

### Get user by username

```
GET /user/{username}
```

Description: Retrieve a user.

Path:
- username

Success:
- 200: User

Errors:
- 400: Invalid username
- 404: User not found
- default

Example:
```
curl http://localhost:3000/api/v3/user/user1
```

---

### Update user

```
PUT /user/{username}
```

Description: Update user resource.

Path:
- username

Body: User

Success:
- 200

Errors:
- 400
- 404
- default

Example:
```
curl -X PUT http://localhost:3000/api/v3/user/user1 \
  -H "Content-Type: application/json" \
  -d '{"firstName":"John"}'
```

---

### Delete user

```
DELETE /user/{username}
```

Description: Delete user.

Path:
- username

Success:
- 200: User deleted

Errors:
- 400
- 404
- default

Example:
```
curl -X DELETE http://localhost:3000/api/v3/user/user1
```

---

## Orchestrator API Contract

None provided.

## Mock Destination API Contract

None provided.