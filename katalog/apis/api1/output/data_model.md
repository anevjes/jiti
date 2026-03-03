# Data Model: api1

**Feature**: api1  
**Date**: 2026-03-03

## Entities

### Pet
Represents an animal in the store, including its metadata, category, images, tags, and status. Used in creation, updates, searches, and retrieval operations.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer int64 | no | Unique identifier for the pet. |
| name | string | yes | Name of the pet. |
| category | Category | no | The category this pet belongs to. |
| photoUrls | array[string] | yes | URLs to images of the pet. |
| tags | array[Tag] | no | Tags associated with the pet. |
| status | string | no | Pet’s availability in the store: available, pending, sold. |

**Validation rules**:
- name must be a non-empty string.
- photoUrls must contain at least one item.
- status must be one of available, pending, sold.

---

### Category
Represents a classification for pets.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer int64 | no | Unique identifier for the category. |
| name | string | no | Name of the category. |

---

### Tag
A simple label that can be associated with pets.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer int64 | no | Tag identifier. |
| name | string | no | Tag name. |

---

### Order
Represents a purchase order placed for a pet.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer int64 | no | Order ID. |
| petId | integer int64 | no | ID of the pet being ordered. |
| quantity | integer int32 | no | Number of items ordered. |
| shipDate | string date-time | no | Shipping date. |
| status | string | no | Order status: placed, approved, delivered. |
| complete | boolean | no | Indicates if the order is complete. |

**Validation rules**:
- status must be one of placed, approved, delivered.
- quantity must be a non-negative integer (inferred).

---

### User
Represents a user account in the system.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer int64 | no | User ID. |
| username | string | no | Username of the user. |
| firstName | string | no | First name. |
| lastName | string | no | Last name. |
| email | string | no | Email address. |
| password | string | no | Password. |
| phone | string | no | Phone number. |
| userStatus | integer int32 | no | User status code. |

**Validation rules**:
- email must be a valid email format (inferred).
- password must be non-empty when used for login (inferred).

---

### ApiResponse
Generic response model used for upload operations.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| code | integer int32 | no | Status code. |
| type | string | no | Type indicator. |
| message | string | no | Human‑readable message. |

---

### Inventory (inferred)
Returned by GET /store/inventory. Represents a mapping of pet status to inventory count.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| <status> | integer int32 | no | Quantity of pets for a given status. |

---

### LoginResponse (inferred)
Represents the response to a user login.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | no | Login token returned as plain string in response body. |
| X-Rate-Limit | integer int32 | no | Calls per hour allowed (response header). |
| X-Expires-After | string date-time | no | Token expiration timestamp (response header). |

---

## Configuration Files

Example YAML for entities:

```
pet:
  id: 10
  name: "doggie"
  category:
    id: 1
    name: "Dogs"
  photoUrls:
    - "http://example.com/photo1.jpg"
  tags:
    - id: 5
      name: "friendly"
  status: "available"

order:
  id: 100
  petId: 10
  quantity: 2
  shipDate: "2026-03-10T12:00:00Z"
  status: "placed"
  complete: false

user:
  id: 20
  username: "theUser"
  firstName: "John"
  lastName: "James"
  email: "john@email.com"
  password: "12345"
  phone: "12345"
  userStatus: 1
```

Example `.env` style (inferred for configs):

```
API_KEY=your-key-here
PETSTORE_AUTH_TOKEN=your-oauth-token
```

## Relationships

```
Pet ──1:1──▶ Category        (A pet may belong to one category)
Pet ──1:N──▶ Tag             (A pet can have multiple tags)

Order ──1:1──▶ Pet           (Order references one pet via petId)

User ──N:1──▶ (System)       (Users exist independently; no direct associations)

Inventory ──(map)──▶ Pet     (Inventory keyed by pet status, inferred)

LoginResponse ──1:1──▶ User  (Login response corresponds to login attempt for a user, inferred)
```