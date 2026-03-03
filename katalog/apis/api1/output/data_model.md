# Data Model: api1

**Feature**: api1  
**Date**: 2026-03-03

## Entities

### Pet

Represents an animal in the store, including metadata such as its category, photos, and tags. Pets can be created, updated, retrieved, deleted, and filtered by status or tag.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | Unique identifier for the pet. |
| name | string | yes | Name of the pet. |
| category | Category | no | Category the pet belongs to. |
| photoUrls | array of string | yes | List of photo URLs. |
| tags | array of Tag | no | Tags associated with the pet. |
| status | string | no | Pet status in the store. Enum: available, pending, sold. |

**Validation rules**:
- name must be a non‑empty string.
- photoUrls must contain at least one item.
- status must be one of: available, pending, sold.

---

### Category

Represents a grouping for pets such as "Dogs" or "Cats".

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | Unique category ID. |
| name | string | no | Category name. |

---

### Tag

Represents labels that can be assigned to pets for filtering.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | Tag identifier. |
| name | string | no | Tag name. |

---

### ApiResponse

Generic response wrapper used for file upload responses.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| code | integer (int32) | no | Status or error code. |
| type | string | no | Type of message. |
| message | string | no | Additional human‑readable message. |

---

### Order

Represents a purchase order in the store.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | Order ID. |
| petId | integer (int64) | no | Identifier of the pet being ordered. |
| quantity | integer (int32) | no | Quantity ordered. |
| shipDate | string (date-time) | no | Shipment date. |
| status | string | no | Order status. Enum: placed, approved, delivered. |
| complete | boolean | no | Whether the order is complete. |

**Validation rules**:
- status must be one of: placed, approved, delivered.

**State transitions** (inferred):
- placed → approved → delivered.

---

### Inventory (inferred runtime entity)

Represents a map of pet status to available inventory counts as returned by `/store/inventory`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| <status> | integer | no | Quantity of pets in the given status (dynamic keys). |

---

### User

Represents an account in the system, with basic personal and authentication fields.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | User identifier. |
| username | string | no | Login username. |
| firstName | string | no | User’s first name. |
| lastName | string | no | User’s last name. |
| email | string | no | Email address. |
| password | string | no | Password in clear text. |
| phone | string | no | Phone number. |
| userStatus | integer (int32) | no | User status code. |

**Validation rules**:
- email should be a valid email format (inferred).
- password should not be empty (inferred).

---

### LoginResponse (inferred)

Response for `/user/login`, consisting of a string token plus rate‑limit headers.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | no | Session token returned as response body. |
| X-Rate-Limit | integer (int32) | no | Calls per hour allowed. |
| X-Expires-After | string (date-time) | no | UTC expiration timestamp. |

---

### UploadFileRequest (inferred)

Binary image upload request for a pet.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | binary | no | Image file to upload. |
| additionalMetadata | string | no | Additional metadata for the image upload. |

---

## Configuration Files

YAML example representing core schemas:

```yaml
pet:
  id: 10
  name: doggie
  category:
    id: 1
    name: Dogs
  photoUrls:
    - https://example.com/dog1.jpg
  tags:
    - id: 100
      name: friendly
  status: available

order:
  id: 55
  petId: 10
  quantity: 2
  shipDate: "2026-03-03T12:00:00Z"
  status: approved
  complete: false

user:
  id: 10
  username: theUser
  firstName: John
  lastName: James
  email: john@email.com
  password: "12345"
  phone: "12345"
  userStatus: 1

inventory:
  available: 20
  pending: 5
  sold: 3
```

Environment variables (inferred):

```
API_KEY=your-api-key-here
OAUTH_AUTH_URL=https://petstore3.swagger.io/oauth/authorize
```

## Relationships

```
Pet ──0:1──▶ Category    (a pet may belong to one category)
Pet ──0:*──▶ Tag         (a pet may have multiple tags)

Order ──1:1──▶ Pet       (order references a single pet by petId)

Inventory ──dynamic──▶ Pet.status   (inventory keys correspond to pet statuses)

User ──independent──▶ (no direct object links in API)
```
