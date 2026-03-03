# Data Model: api1

**Feature**: api1  
**Date**: 2026-03-03

## Entities

### Pet  
Represents an animal available in the store. Includes identification, categorization, photos, tags, and lifecycle status.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | Unique identifier for the pet. |
| name | string | yes | Name of the pet. |
| category | Category | no | Category the pet belongs to. |
| photoUrls | array of string | yes | List of URLs to pet photos. |
| tags | array of Tag | no | Tags associated with the pet. |
| status | string | no | Pet status in the store (available, pending, sold). |

**Validation rules**:
- name must be non-empty.
- photoUrls must contain at least one item.
- status must be one of: available, pending, sold.

---

### Category  
Represents a classification for pets.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | Category identifier. |
| name | string | no | Category name. |

**Validation rules**:
- name should be non-empty (inferred).

---

### Tag  
Represents a label/tag assigned to a pet.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | Tag identifier. |
| name | string | no | Tag name. |

**Validation rules**:
- name should be non-empty (inferred).

---

### Order  
Represents a purchase order for a pet.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | Order identifier. |
| petId | integer (int64) | no | ID of the pet being ordered. |
| quantity | integer (int32) | no | Number of pets ordered. |
| shipDate | string (date-time) | no | Shipment timestamp. |
| status | string | no | Order status (placed, approved, delivered). |
| complete | boolean | no | Whether the order is complete. |

**Validation rules**:
- quantity must be >= 0 (inferred).
- status must be one of: placed, approved, delivered.
- shipDate must be valid ISO-8601 (inferred).

---

### User  
Represents a system user profile.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer (int64) | no | User identifier. |
| username | string | no | User login name. |
| firstName | string | no | First name. |
| lastName | string | no | Last name. |
| email | string | no | Email address. |
| password | string | no | Password (plaintext in API). |
| phone | string | no | Phone number. |
| userStatus | integer (int32) | no | User status code. |

**Validation rules**:
- username must be unique (inferred).
- email should be a valid email format (inferred).
- password should be non-empty (inferred).

---

### ApiResponse  
Generic response wrapper for file uploads and other operations.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| code | integer (int32) | no | Status/error code. |
| type | string | no | Response type string. |
| message | string | no | Human-readable message. |

**Validation rules**:
- none beyond type constraints.

---

### Inventory (inferred entity)  
Represents a map of pet statuses to item counts, returned by `/store/inventory`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| <status> | integer (int32) | no | Quantity for the given status key. |

**Validation rules**:
- keys are expected to correspond to Pet status values (inferred).

---

### UploadImageRequest (inferred)  
Represents the upload request sent to `/pet/{petId}/uploadImage`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| petId | integer (int64) | yes | ID of the pet whose image is being uploaded. |
| additionalMetadata | string | no | Optional metadata string. |
| file | binary | yes | Image file binary payload. |

**Validation rules**:
- file must be provided.
- petId must be a valid numeric identifier.

---

## Configuration Files

### Example YAML for Pet
```
id: 42
name: "Fluffy"
category:
  id: 2
  name: "Cats"
photoUrls:
  - "https://example.com/photos/fluffy1.jpg"
tags:
  - id: 99
    name: "cute"
status: "available"
```

### Example YAML for Order
```
id: 1001
petId: 42
quantity: 1
shipDate: "2026-03-04T10:00:00Z"
status: "placed"
complete: false
```

### Example YAML for User
```
id: 501
username: "jdoe"
firstName: "John"
lastName: "Doe"
email: "jdoe@example.com"
password: "secret"
phone: "123-456-7890"
userStatus: 1
```

### Example Inventory
```
available: 12
pending: 3
sold: 8
```

### Example UploadImageRequest environment variables
```
PET_ID=42
ADDITIONAL_METADATA="taken in March"
FILE_PATH="./fluffy.png"
```

## Relationships

```
Pet ──0..1──▶ Category     (A pet can belong to one category.)
Pet ──0..*──▶ Tag          (A pet can have multiple tags.)
Order ──1──▶ Pet           (Order references a pet by petId.)
User ──(independent entity)── (No direct links to pets or orders in swagger.)
Inventory ──keyed-by──▶ Pet.status   (Keys correspond to pet status values.)
UploadImageRequest ──1──▶ Pet        (Upload is tied to a specific pet ID.)
```