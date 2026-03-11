# Data Model: api1 (Petstore API)

**Feature**: api1  
**Date**: 2026-03-11

---

## Entities

### Pet

Represents an individual pet that can be offered for sale in the store, including its identity, classification, photos, tags, and availability status.

| Field      | Type                    | Required | Description |
|-----------|-------------------------|----------|-------------|
| id        | integer(int64)          | no       | Unique identifier of the pet in the store. Often assigned by the system. |
| name      | string                  | yes      | Display name of the pet (e.g., "Fido", "Snowball"). |
| category  | Category                | no       | Category of the pet (e.g., Dogs, Cats) used for high-level classification. |
| photoUrls | string[]                | yes      | List of URLs pointing to images of the pet. Must contain at least one URL. |
| tags      | Tag[]                   | no       | List of tags describing or grouping the pet (e.g., "small", "adopted"). |
| status    | string (enum)           | no       | Current lifecycle status of the pet in the store. One of: `available`, `pending`, `sold`. |

**Validation rules**:
- `name` must be non-empty text.
- `photoUrls` must be a non-empty array; each item should be a valid URL string (inferred).
- `status`, if provided, must be one of: `available`, `pending`, `sold`.
- `id`, if provided, must be a positive 64-bit integer (inferred).
- `category.id`, `tags[].id` (if present) are positive 64-bit integers (inferred).

**State transitions** (business-level, as implied by API):
- `available` → `pending`: when a pet is reserved or an in-progress order exists (inferred).
- `pending` → `sold`: when an order is completed and the pet is no longer available.
- `available`/`pending`/`sold` → (deleted): when `DELETE /pet/{petId}` is called; pet is removed from the catalog.

---

### Category

Represents a high-level classification for pets (such as Dogs, Cats, Birds), used to organize the catalog.

| Field | Type           | Required | Description |
|-------|----------------|----------|-------------|
| id    | integer(int64) | no       | Unique identifier of the category. |
| name  | string         | no       | Human-readable category name (e.g., "Dogs"). |

**Validation rules**:
- `id`, if provided, must be a positive 64-bit integer (inferred).
- `name`, if provided, should be non-empty and unique within categories (inferred).

---

### Tag

Represents a free-form label used to group or annotate pets for search and reporting purposes.

| Field | Type           | Required | Description |
|-------|----------------|----------|-------------|
| id    | integer(int64) | no       | Unique identifier of the tag. |
| name  | string         | no       | Name of the tag (e.g., "puppy", "vaccinated"). |

**Validation rules**:
- `id`, if provided, must be a positive 64-bit integer (inferred).
- `name`, if provided, should be non-empty and unique within tags for a given tenant/store (inferred).

---

### Order

Represents a purchase order for a specific pet, including quantities, shipping information, and lifecycle status.

| Field    | Type               | Required | Description |
|----------|--------------------|----------|-------------|
| id       | integer(int64)     | no       | Unique identifier of the order. |
| petId    | integer(int64)     | no       | Identifier of the pet being ordered, referencing `Pet.id`. |
| quantity | integer(int32)     | no       | Quantity of this pet ordered (typically `1`; supports bulk scenarios). |
| shipDate | string(date-time)  | no       | Date-time when the order is scheduled to ship or actually shipped. |
| status   | string (enum)      | no       | Order lifecycle status (`placed`, `approved`, `delivered`). |
| complete | boolean            | no       | Flag indicating whether the order is considered fully complete. |

**Validation rules**:
- `id`, if provided, must be a positive 64-bit integer (inferred).
- `petId`, if provided, must be a positive 64-bit integer referencing an existing Pet (inferred).
- `quantity`, if provided, must be a positive 32-bit integer (inferred).
- `shipDate`, if provided, must be a valid ISO 8601 date-time string.
- `status`, if provided, must be one of: `placed`, `approved`, `delivered`.
- `complete`, if provided, must be boolean.

**State transitions** (inferred from enum and business guide):
- `placed` → `approved`: after validation/acceptance of the order.
- `approved` → `delivered`: when the pet has been delivered to the customer.
- Orders can be deleted (`DELETE /store/order/{orderId}`) while in any state; business rules may restrict deletion to `placed` or `approved` in real implementations (inferred).

---

### InventorySnapshot

Represents the current quantity of pets in each availability status as returned by the inventory endpoint.

| Field                    | Type                    | Required | Description |
|--------------------------|-------------------------|----------|-------------|
| [statusCode] (dynamic)   | integer(int32)          | no       | For each status key (e.g., `available`, `pending`, `sold`), the number of pets currently in that state. Keys are strings; values are counts. |

**Notes**:
- This is represented as a JSON object where each property name is a status code and the value is an integer count (e.g., `{ "available": 42, "sold": 5 }`).
- Keys are not restricted in the schema but are typically the same as `Pet.status` values (inferred from docs).

**Validation rules**:
- Each value must be a non-negative 32-bit integer (inferred).
- Keys should be consistent with `Pet.status` enumerations when representing standard inventory (`available`, `pending`, `sold`) (inferred).

---

### User

Represents a person (customer or staff) who can interact with the system and whose profile is managed via the API.

| Field      | Type           | Required | Description |
|------------|----------------|----------|-------------|
| id         | integer(int64) | no       | Unique identifier of the user. |
| username   | string         | no       | Unique login and lookup name of the user. |
| firstName  | string         | no       | User's given name. |
| lastName   | string         | no       | User's family name. |
| email      | string         | no       | Contact email address for the user. |
| password   | string         | no       | User's password in clear text as sent to the API (demo-only practice). |
| phone      | string         | no       | Contact phone number for the user. |
| userStatus | integer(int32) | no       | Application-specific status code for the user (e.g., active, inactive, banned) (inferred from description). |

**Validation rules**:
- `id`, if provided, must be a positive 64-bit integer (inferred).
- `username`, if provided, should be unique within the system and non-empty (inferred).
- `email`, if provided, should be a valid email address format (inferred).
- `password`, if provided, should satisfy minimum length and complexity policies in real deployments (inferred).
- `userStatus`, if provided, should be a valid status code defined by the hosting system; typical usage might be: `0=inactive`, `1=active`, etc. (inferred).
- When used for login (`/user/login`), `username` and `password` parameters must match an existing user record (inferred).

**State transitions** (inferred):
- User profile data (e.g., name, email, phone, password, `userStatus`) can be updated via `PUT /user/{username}`.
- User can effectively transition from "present" → "deleted" when `DELETE /user/{username}` is called.

---

### ApiResponse

Represents a generic API-level response used by operations like image upload to return codes, types, and messages.

| Field   | Type           | Required | Description |
|---------|----------------|----------|-------------|
| code    | integer(int32) | no       | Numeric status or result code (application-level). |
| type    | string         | no       | Short classification or type of the response (e.g., "success", "error") (inferred). |
| message | string         | no       | Human-readable message providing additional detail about the result. |

**Validation rules**:
- `code`, if provided, must be a valid 32-bit integer.
- `type`, if provided, should be a short, non-empty string (inferred).
- `message`, if provided, should be a human-readable description; may be used for UI/display (inferred).

---

### PetUploadRequest

Represents the data involved when a client uploads a binary image file for a specific pet.

| Field              | Type             | Required | Description |
|--------------------|------------------|----------|-------------|
| petId              | integer(int64)   | yes      | Identifier of the pet whose image is being uploaded. |
| additionalMetadata | string           | no       | Textual metadata associated with the uploaded image (e.g., caption, source). |
| file               | binary           | no       | Binary image data sent as `application/octet-stream` in the request body. |

**Validation rules**:
- `petId` must be a positive 64-bit integer.
- `additionalMetadata`, if provided, should be short text (inferred).
- `file` should not be empty for a successful upload; absence leads to "No file uploaded" error.
- Uploaded file should conform to allowed file size and image types (e.g., JPEG, PNG) depending on implementation (inferred).

---

### PetSearchByStatusRequest

Represents the query parameters used to search pets by availability status.

| Field  | Type               | Required | Description |
|--------|--------------------|----------|-------------|
| status | string (enum)      | yes      | Status values to filter pets. Single string that may encode multiple comma-separated values. Allowed values: `available`, `pending`, `sold`. Default is `available`. |

**Validation rules**:
- `status` must not be empty.
- Each status token (after splitting on commas) must be one of: `available`, `pending`, `sold` (inferred from description).
- If invalid value is provided, API returns "Invalid status value".

---

### PetSearchByTagsRequest

Represents the query parameters used to search pets by tags.

| Field | Type       | Required | Description |
|-------|------------|----------|-------------|
| tags  | string[]   | yes      | One or more tag values to filter pets by. Can be provided as repeated query parameters or comma-separated strings. |

**Validation rules**:
- `tags` must contain at least one tag value.
- Individual tag values should be non-empty strings.
- If invalid tag values are provided (e.g., unsupported format), "Invalid tag value" is returned (inferred).

---

### PetUpdateWithFormRequest

Represents the parameters used when updating a pet’s basic details via the `updatePetWithForm` operation.

| Field | Type           | Required | Description |
|-------|----------------|----------|-------------|
| petId | integer(int64) | yes      | Identifier of the pet to update. |
| name  | string         | no       | New name for the pet. If omitted, name is unchanged. |
| status| string         | no       | New status for the pet. Same allowed values as `Pet.status`. |

**Validation rules**:
- `petId` must be a positive 64-bit integer.
- `name`, if provided, must be non-empty.
- `status`, if provided, must be one of: `available`, `pending`, `sold`.
- Attempting to update a non-existing `petId` results in "Pet not found" (inferred from similar operations).

---

### CreateUserRequest

Represents the payload used when creating a single user.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| body  | User | yes      | User object to be created. |

**Validation rules**:
- Same field-level rules as `User`.
- `username` should be unique; creating with an existing username may fail or update depending on implementation (inferred).

---

### CreateUsersWithListRequest

Represents the payload used when creating multiple users in bulk.

| Field | Type    | Required | Description |
|-------|---------|----------|-------------|
| body  | User[]  | yes      | Array of user objects to create. |

**Validation rules**:
- Array must not be empty (inferred).
- Each item must satisfy `User` validation rules.
- Duplicate usernames within the list or compared to existing users may cause errors (inferred).

---

### UserLoginRequest

Represents the query parameters used when logging a user into the system.

| Field    | Type   | Required | Description |
|----------|--------|----------|-------------|
| username | string | no       | Username credential used for login. |
| password | string | no       | Password credential (clear text) used for login. |

**Validation rules**:
- In practice, both `username` and `password` must be provided and non-empty for a successful login (inferred).
- Values must match an existing `User` record; otherwise "Invalid username/password supplied".

---

### UserLoginResponse

Represents the response returned after a successful login, including rate limiting and token expiry information.

| Field           | Type              | Required | Description |
|-----------------|-------------------|----------|-------------|
| body            | string            | no       | Response body containing a session token or login confirmation string (inferred). |
| X-Rate-Limit    | integer(int32)    | no       | HTTP response header specifying calls per hour allowed for the logged-in user. |
| X-Expires-After | string(date-time) | no       | HTTP response header specifying expiration time of the token in UTC. |

**Validation rules**:
- `X-Rate-Limit`, if present, must be a non-negative 32-bit integer.
- `X-Expires-After`, if present, must be a valid ISO 8601 date-time.
- `body` is an opaque string; consumers treat it as a token or informational text (inferred).

---

### UserProfileRequest

Represents operations that act on a user identified by username path parameter (get, update, delete).

| Field    | Type   | Required | Description |
|----------|--------|----------|-------------|
| username | string | yes      | Path identifier for the target user. |

**Validation rules**:
- `username` must identify an existing user for get/update/delete; otherwise "User not found".
- For `PUT /user/{username}`, the request body must be a valid `User` object.

---

### InventoryRequest

Represents the (empty) request to query inventory.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| —     | —    | —        | `GET /store/inventory` does not require query or body fields. |

**Validation rules**:
- None; endpoint is read-only and unauthenticated except for API key, which is handled as a separate concern.

---

## Configuration Files

Below are example configuration snippets (YAML and environment-style) that align with the entities and their usage patterns in the API. These are illustrative for clients/services integrating with the Petstore API.

### Example: Service Configuration for Petstore Client (YAML)

```yaml
petstore:
  baseUrl: "https://petstore3.swagger.io/api/v3"
  # Authentication configuration (inferred, matches security schemes)
  auth:
    apiKey:
      enabled: true
      headerName: "api_key"
      value: "YOUR_API_KEY_HERE"
    oauth2:
      enabled: false
      authorizationUrl: "https://petstore3.swagger.io/oauth/authorize"
      clientId: "your-client-id"         # (inferred)
      clientSecret: "your-client-secret" # (inferred)
      scopes:
        - "write:pets"
        - "read:pets"

  defaults:
    petStatusFilter: "available"  # default for /pet/findByStatus
    orderPageSize: 50             # (inferred; not in API)
    userStatusDefault: 1          # maps to active user (inferred)

  # Example seed data representing the domain entities

  categories:
    - id: 1
      name: "Dogs"
    - id: 2
      name: "Cats"

  tags:
    - id: 1
      name: "small"
    - id: 2
      name: "vaccinated"

  pets:
    - id: 10
      name: "doggie"
      category:
        id: 1
        name: "Dogs"
      photoUrls:
        - "https://cdn.example.com/pets/10-1.jpg"
      tags:
        - id: 1
          name: "small"
        - id: 2
          name: "vaccinated"
      status: "available"

  users:
    - id: 10
      username: "theUser"
      firstName: "John"
      lastName: "James"
      email: "john@email.com"
      password: "12345"
      phone: "12345"
      userStatus: 1

  orders:
    - id: 1001
      petId: 10
      quantity: 1
      shipDate: "2026-03-11T10:30:00Z"
      status: "placed"
      complete: false

  # Example cached inventory snapshot
  inventory:
    available: 25
    pending: 3
    sold: 12
```

### Example: Environment-Style Client Configuration (.env)

```env
# Base connectivity
PETSTORE_BASE_URL=https://petstore3.swagger.io/api/v3

# API key auth
PETSTORE_API_KEY_ENABLED=true
PETSTORE_API_KEY_HEADER_NAME=api_key
PETSTORE_API_KEY_VALUE=YOUR_API_KEY_HERE

# OAuth2 (implicit flow) configuration (if used)
PETSTORE_OAUTH2_ENABLED=false
PETSTORE_OAUTH2_AUTH_URL=https://petstore3.swagger.io/oauth/authorize
PETSTORE_OAUTH2_CLIENT_ID=your-client-id
PETSTORE_OAUTH2_CLIENT_SECRET=your-client-secret
PETSTORE_OAUTH2_SCOPES=write:pets,read:pets

# Default filters / behavior
PETSTORE_DEFAULT_PET_STATUS=available
PETSTORE_DEFAULT_USER_STATUS=1

# Example: operational limits (inferred)
PETSTORE_HTTP_TIMEOUT_MS=5000
PETSTORE_MAX_REQUESTS_PER_MINUTE=50
```

### Example: Pet Creation Request (YAML)

```yaml
# Payload for POST /pet
id: 21
name: "Snowball"
category:
  id: 2
  name: "Cats"
photoUrls:
  - "https://cdn.example.com/pets/21-1.jpg"
tags:
  - id: 3
    name: "white"
  - id: 4
    name: "kitten"
status: "available"
```

### Example: Order Placement Request (YAML)

```yaml
# Payload for POST /store/order
id: 2001
petId: 21
quantity: 1
shipDate: "2026-03-12T09:00:00Z"
status: "placed"
complete: false
```

### Example: User Creation (Single and Bulk) (YAML)

```yaml
# Payload for POST /user
id: 101
username: "alice"
firstName: "Alice"
lastName: "Anderson"
email: "alice@example.com"
password: "secureP@ssw0rd"
phone: "+1-555-0101"
userStatus: 1
```

```yaml
# Payload for POST /user/createWithList
- id: 102
  username: "bob"
  firstName: "Bob"
  lastName: "Brown"
  email: "bob@example.com"
  password: "pass123"
  phone: "+1-555-0102"
  userStatus: 1
- id: 103
  username: "carol"
  firstName: "Carol"
  lastName: "Clark"
  email: "carol@example.com"
  password: "pass456"
  phone: "+1-555-0103"
  userStatus: 1
```

---

## Relationships

```text
Pet ──1:1──▶ Category
  A pet belongs to at most one category; a category can classify many pets.

Pet ──1:N──▶ Tag
  A pet can have multiple tags; each tag can be reused across many pets (many-to-many in practice).

Order ──N:1──▶ Pet
  Each order references a single pet via petId; a pet can be referenced by multiple orders over time.

InventorySnapshot ──aggregates──▶ Pet
  Inventory counts are derived from the number of pets in each status (available/pending/sold).

User ──authenticates──▶ API Operations
  A user’s credentials (username/password) are used to obtain a session via /user/login and drive access control.

PetUploadRequest ──N:1──▶ Pet
  Each image upload is associated with a single pet identified by petId.

CreateUsersWithListRequest ──N:1──▶ User
  Bulk creation request contains multiple User entities to be persisted.

UserLoginResponse ──describes──▶ User session
  Encapsulates token-related metadata (rate limit and expiry) for the authenticated user.
```