# SDK Proxy API Contract

**Feature**: api1  
**Date**: 2026-03-03  
**Component**: /api1/sdk-proxy

## Base URL

Local: http://localhost:3000/api1  
Debug: http://localhost:3000/debug/api1

---

## Endpoints

(Each endpoint mirrors the provided Petstore OpenAPI contract at `/api/v3/...`.)

Because of the extremely large number of endpoints, and to fit the structure, each API operation is documented below with:

- Title = summary  
- Method + path  
- Description  
- Path/query parameters  
- Forwarding rules: SDK simply proxies through the request to the upstream Petstore backend  
- Success / error responses  
- Example requests/responses  

---

### Update an existing pet

```
PUT /pet
```

Description: Update an existing pet by ID.

Path params: none.

Request forwarding: Body forwarded verbatim as JSON/XML/form.  
Response forwarding: Pass-through of upstream body & status code.

Success responses:
- 200: Pet updated (Pet)

Error responses:
- 400: Invalid ID supplied  
- 404: Pet not found  
- 422: Validation exception  
- default: Unexpected error

Example curl:
```
curl -X PUT http://localhost:3000/api1/pet \
  -H "Content-Type: application/json" \
  -d '{"id":10,"name":"doggie","photoUrls":["url1"]}'
```

Example response:
```
200 OK
{"id":10,"name":"doggie","photoUrls":["url1"]}
```

---

### Add a new pet to the store

```
POST /pet
```

Description: Add a new pet.

Request/response forwarding: direct.

Success: 200 Pet  
Errors: 400 invalid input, 422 validation error, default unexpected

Example curl:
```
curl -X POST http://localhost:3000/api1/pet \
  -H "Content-Type: application/json" \
  -d '{"name":"newpet","photoUrls":["a"]}'
```

---

### Find pets by status

```
GET /pet/findByStatus?status={status}
```

Query:
- status (required) string enum: available, pending, sold

Success: 200 array of Pet  
Error: 400 invalid status, default unexpected

Example:
```
curl http://localhost:3000/api1/pet/findByStatus?status=available
```

---

### Find pets by tags

```
GET /pet/findByTags?tags={tag1,tag2}
```

Query:
- tags (required) array of string

Success: 200 array of Pet  
Error: 400 invalid tag

Example:
```
curl "http://localhost:3000/api1/pet/findByTags?tags=tag1&tags=tag2"
```

---

### Find pet by ID

```
GET /pet/{petId}
```

Path:
- petId (integer)

Success: 200 Pet  
Errors: 400 invalid ID, 404 not found

Example:
```
curl http://localhost:3000/api1/pet/10
```

---

### Update pet with form

```
POST /pet/{petId}?name={name}&status={status}
```

Query: name, status optional  
Path: petId

Success: 200 Pet  
Error: 400 invalid input

---

### Delete a pet

```
DELETE /pet/{petId}
```

Headers: optional api_key  
Path: petId

Success: 200 Pet deleted  
Errors: 400 invalid value

---

### Upload pet image

```
POST /pet/{petId}/uploadImage
```

Path: petId  
Query: additionalMetadata optional  
Body: binary file

Success: 200 ApiResponse  
Errors: 400 no file, 404 pet not found

---

### Get store inventory

```
GET /store/inventory
```

Success: 200 map<string,int>

---

### Place order

```
POST /store/order
```

Body: Order

Success: 200 Order  
Errors: 400 invalid input, 422 validation

---

### Get order by ID

```
GET /store/order/{orderId}
```

Path: orderId

Success: 200 Order  
Error: 400 invalid ID, 404 not found

---

### Delete order

```
DELETE /store/order/{orderId}
```

Success: 200 order deleted  
Errors: 400 invalid ID, 404 not found

---

### Create user

```
POST /user
```

Body: User

Success: 200 User

---

### Create users with list

```
POST /user/createWithList
```

Body: array<User>

Success: 200 User

---

### Login user

```
GET /user/login?username={u}&password={p}
```

Success: 200 string  
Headers: X-Rate-Limit, X-Expires-After  
Error: 400 invalid credentials

---

### Logout user

```
GET /user/logout
```

Success: 200

---

### Get user by username

```
GET /user/{username}
```

Success: 200 User  
Error: 400 invalid username, 404 not found

---

### Update user

```
PUT /user/{username}
```

Body: User

Success: 200  
Error: 400 bad request, 404 not found

---

### Delete user

```
DELETE /user/{username}
```

Success: 200  
Error: 400 invalid username, 404 not found

---

## Orchestrator API Contract

No orchestrator is defined in the supplied documentation.

## Mock Destination API Contract

No mock services are defined.