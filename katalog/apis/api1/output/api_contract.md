Below is your SDK Proxy API Contract, generated strictly from the provided Swagger specification.

---

# SDK Proxy API Contract

**Feature**: api1  
**Date**: 2026-03-03  
**Component**: /api/v3

## Base URL

Local: http://localhost:8080/api/v3  
Debug: http://localhost:3000/api/v3

---

## Endpoints

Each of the following endpoints must be exposed by the SDK proxy.  
All requests are forwarded transparently to the destination Petstore API with no request/response transformation unless otherwise noted.

---

### Update Existing Pet

```
PUT /pet
```

Updates an existing pet by ID (provided inside the body).

Path parameters:  
None.

Request forwarding:  
• Forward body exactly as received (JSON, XML, or form).  
• Forward authentication headers if supplied.

Success response:  
• 200: Pet object returned.

Error responses:  
• 400 Invalid ID supplied  
• 404 Pet not found  
• 422 Validation exception  
• default Unexpected error

Example cURL:

```
curl -X PUT http://localhost:8080/api/v3/pet \
  -H "Content-Type: application/json" \
  -d '{"id":10,"name":"doggie","photoUrls":["url"],"status":"available"}'
```

---

### Add New Pet

```
POST /pet
```

Adds a new pet to the store.

Path parameters:  
None.

Request forwarding:  
• Forward body exactly.  
• Authentication forwarded.

Success:  
• 200 Pet object returned.

Errors:  
• 400 Invalid input  
• 422 Validation exception  
• default Unexpected error

Example:

```
curl -X POST http://localhost:8080/api/v3/pet \
  -H "Content-Type: application/json" \
  -d '{"name":"doggie","photoUrls":["url"]}'
```

---

### Find Pets by Status

```
GET /pet/findByStatus
```

Returns pets filtered by one or more statuses.

Query parameters:  
• status (required, enum: available, pending, sold)

Example: `?status=available,pending`

Success:  
• 200 Array of Pet objects.

Errors:  
• 400 Invalid status value  
• default Unexpected error

Example:

```
curl http://localhost:8080/api/v3/pet/findByStatus?status=available
```

---

### Find Pets by Tags

```
GET /pet/findByTags
```

Returns pets filtered by tags.

Query parameters:  
• tags (array, required)

Success:  
• 200 Array of Pet objects.

Errors:  
• 400 Invalid tag value  
• default Unexpected error

Example:

```
curl http://localhost:8080/api/v3/pet/findByTags?tags=tag1&tags=tag2
```

---

### Get Pet by ID

```
GET /pet/{petId}
```

Returns a single pet.

Path parameters:  
• petId (int64, required)

Success:  
• 200 Pet object.

Errors:  
• 400 Invalid ID supplied  
• 404 Pet not found  
• default Unexpected error

Example:

```
curl http://localhost:8080/api/v3/pet/10
```

---

### Update Pet With Form

```
POST /pet/{petId}
```

Updates basic pet information using form-like parameters in query.

Path parameters:  
• petId (int64, required)

Query parameters:  
• name (string)  
• status (string)

Success:  
• 200 Pet object

Errors:  
• 400 Invalid input  
• default Unexpected error

Example:

```
curl -X POST "http://localhost:8080/api/v3/pet/10?name=Fluffy&status=available"
```

---

### Delete Pet

```
DELETE /pet/{petId}
```

Deletes a pet.

Path parameters:  
• petId (int64, required)

Headers:  
• api_key (optional)

Success:  
• 200 Pet deleted

Errors:  
• 400 Invalid pet value  
• default Unexpected error

Example:

```
curl -X DELETE http://localhost:8080/api/v3/pet/10 -H "api_key: secret"
```

---

### Upload Pet Image

```
POST /pet/{petId}/uploadImage
```

Uploads a binary image for a pet.

Path parameters:  
• petId (int64, required)

Query parameters:  
• additionalMetadata (string, optional)

Body:  
• application/octet-stream (binary)

Success:  
• 200 ApiResponse

Errors:  
• 400 No file uploaded  
• 404 Pet not found  
• default Unexpected error

Example:

```
curl -X POST http://localhost:8080/api/v3/pet/10/uploadImage \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@photo.jpg"
```

---

### Get Store Inventory

```
GET /store/inventory
```

Fetches inventory counts by pet status.

Path parameters: none.

Success:  
• 200 JSON object mapping statuses to integer counts.

Errors:  
• default Unexpected error

Example:

```
curl http://localhost:8080/api/v3/store/inventory
```

---

### Place Order

```
POST /store/order
```

Places an order for a pet.

Body contains Order object.

Success:  
• 200 Order returned.

Errors:  
• 400 Invalid input  
• 422 Validation exception  
• default Unexpected error

Example:

```
curl -X POST http://localhost:8080/api/v3/store/order \
  -H "Content-Type: application/json" \
  -d '{"petId":198772,"quantity":1}'
```

---

### Get Order by ID

```
GET /store/order/{orderId}
```

Retrieves order details.

Path parameters:  
• orderId (int64, required)

Success:  
• 200 Order

Errors:  
• 400 Invalid ID supplied  
• 404 Order not found  
• default Unexpected error

Example:

```
curl http://localhost:8080/api/v3/store/order/5
```

---

### Delete Order

```
DELETE /store/order/{orderId}
```

Deletes an order.

Path parameters:  
• orderId (int64, required)

Success:  
• 200 order deleted

Errors:  
• 400 Invalid ID supplied  
• 404 Order not found  
• default Unexpected error

Example:

```
curl -X DELETE http://localhost:8080/api/v3/store/order/5
```

---

### Create User

```
POST /user
```

Creates a new user.

Content types supported: JSON, XML, form.

Success:  
• 200 User object

Errors:  
• default Unexpected error

Example:

```
curl -X POST http://localhost:8080/api/v3/user \
  -H "Content-Type: application/json" \
  -d '{"username":"theUser","firstName":"John"}'
```

---

### Create Users with List Input

```
POST /user/createWithList
```

Creates multiple users.

Body: array of User objects.

Success:  
• 200 User

Errors:  
• default Unexpected error

Example:

```
curl -X POST http://localhost:8080/api/v3/user/createWithList \
  -H "Content-Type: application/json" \
  -d '[{"username":"u1"},{"username":"u2"}]'
```

---

### Login User

```
GET /user/login
```

Logs user into the system.

Query parameters:  
• username (string)  
• password (string)

Success:  
• 200 String response  
• Headers: X-Rate-Limit, X-Expires-After

Errors:  
• 400 Invalid username/password supplied  
• default Unexpected error

Example:

```
curl "http://localhost:8080/api/v3/user/login?username=theUser&password=12345"
```

---

### Logout User

```
GET /user/logout
```

Logs out the current session.

Success:  
• 200 successful operation

Errors:  
• default Unexpected error

Example:

```
curl http://localhost:8080/api/v3/user/logout
```

---

### Get User by Username

```
GET /user/{username}
```

Retrieves a user's details.

Path parameters:  
• username (string, required)

Success:  
• 200 User

Errors:  
• 400 Invalid username supplied  
• 404 User not found  
• default Unexpected error

Example:

```
curl http://localhost:8080/api/v3/user/user1
```

---

### Update User

```
PUT /user/{username}
```

Updates an existing user.

Path parameters:  
• username (string, required)

Body: User object.

Success:  
• 200 successful operation

Errors:  
• 400 bad request  
• 404 user not found  
• default Unexpected error

Example:

```
curl -X PUT http://localhost:8080/api/v3/user/theUser \
  -H "Content-Type: application/json" \
  -d '{"firstName":"Jane"}'
```

---

### Delete User

```
DELETE /user/{username}
```

Deletes a user.

Path parameters:  
• username (string, required)

Success:  
• 200 User deleted

Errors:  
• 400 Invalid username  
• 404 User not found  
• default Unexpected error

Example:

```
curl -X DELETE http://localhost:8080/api/v3/user/theUser
```

---

## Orchestrator API Contract

No orchestrator is defined in supplied documentation. None included.

## Mock Destination API Contract

No mock/demo destinations are defined. None included.

---