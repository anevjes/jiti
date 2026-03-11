# Data Model: api1

**Feature**: api1
**Date**: 2026-03-11

## Entities

### Pet

Represents an individual pet that can be listed, searched, sold, and removed from the store. Pets are categorized, can have multiple photos, and can be tagged for flexible grouping and search.

| Field      | Type              | Required | Description |
|-----------|-------------------|----------|-------------|
| id        | integer (int64)   | No       | Unique identifier for the pet in the store. Usually assigned by the system. |
| name      | string            | Yes      | Name of the pet as displayed to users. |
| category  | Category          | No       | Category to which this pet belongs (e.g., Dogs, Cats). |
| photoUrls | string[]          | Yes      | List of URLs pointing to photos for this pet. |
| tags      | Tag[]             | No       | List of tags for flexible grouping and searching (e.g., “puppy”, “small”). |
| status    | string (enum)     | No       | Pet status in the store: `available`, `pending`, or `sold`. |

**Validation rules**:
- `name`:
  - Must be non-empty.
- `photoUrls`:
  - Must contain at least one item.
  - Each entry must be a non-empty string (URL format inferred).
- `status`:
  - If present, must be one of: `available`, `pending`, `sold`.
- `id`:
  - When provided, must be a positive 64-bit integer (inferred).
- `category`:
  - If provided, must be a valid `Category` object.
- `tags`:
  - If provided, each element must be a valid `Tag` object.

**State transitions** (status):
- `available` → `pending` → `sold`
- `available` → `sold` (direct sale, inferred)
- Transitions from `sold` back to `available` or `pending` should be avoided (inferred business rule; may be reserved for corrections only).

---

### Category

Represents a high-level classification for pets (e.g., Dogs, Cats). Used mainly for grouping and reporting.

| Field | Type            | Required | Description |
|-------|-----------------|----------|-------------|
| id    | integer (int64) | No       | Unique identifier for the category. |
| name  | string          | No       | Human-readable category name (e.g., “Dogs”). |

**Validation rules**:
- `id`:
  - If provided, must be a positive 64-bit integer (inferred).
- `name`:
  - If provided, must be a non-empty string (inferred).

---

### Tag

Represents a flexible label that can be associated with pets for grouping, search, or marketing campaigns.

| Field | Type            | Required | Description |
|-------|-----------------|----------|-------------|
| id    | integer (int64) | No       | Unique identifier for the tag. |
| name  | string          | No       | Tag label (e.g., “puppy”, “on-sale”). |

**Validation rules**:
- `id`:
  - If provided, must be a positive 64-bit integer (inferred).
- `name`:
  - If provided, must be a non-empty string (inferred).

---

### Order

Represents a customer purchase order for a specific pet, including quantity, shipping date, and lifecycle status. Used for order placement, tracking, and cancellation.

| Field   | Type              | Required | Description |
|---------|-------------------|----------|-------------|
| id      | integer (int64)   | No       | Unique identifier for the order. Used as the reference number for tracking. |
| petId   | integer (int64)   | No       | Identifier of the pet being ordered. Must reference an existing `Pet`. |
| quantity| integer (int32)   | No       | Number of items ordered (typically 1 for a pet store; higher values may indicate bulk or accessory sales, inferred). |
| shipDate| string (date-time)| No       | Date and time when the order is scheduled to ship. |
| status  | string (enum)     | No       | Order status: `placed`, `approved`, or `delivered`. |
| complete| boolean           | No       | Flag indicating whether the order is fully processed and closed. |

**Validation rules**:
- `id`:
  - If provided, must be a positive 64-bit integer (inferred).
- `petId`:
  - If provided, must be a positive 64-bit integer (inferred).
- `quantity`:
  - If provided, must be a positive 32-bit integer (inferred).
- `shipDate`:
  - If provided, must be a valid ISO 8601 date-time string.
- `status`:
  - If provided, must be one of: `placed`, `approved`, `delivered`.
- `complete`:
  - Boolean; if omitted, defaults to `false` (inferred).

**State transitions** (status):
- `placed` → `approved` → `delivered`
- Cancellation (inferred):
  - A deleted order is conceptually a transition from any state to a “cancelled” terminal state, but this is represented by removal via API rather than a status value.

---

### InventorySnapshot

Represents a dynamic view of current inventory counts, grouped by pet status. The structure is a map from status code to quantity.

| Field            | Type                      | Required | Description |
|------------------|---------------------------|----------|-------------|
| <statusKey>      | integer (int32)           | No       | Key is a string (typically `available`, `pending`, `sold` – inferred); value is the count of pets in that status. |

**Validation rules**:
- Object keys:
  - Any string key is allowed; typical keys are `available`, `pending`, `sold` (inferred).
- Values:
  - Each value must be a non-negative 32-bit integer.

**State transitions**:
- Inventory counts change in response to:
  - Pet creation or deletion.
  - Pet status updates (`available` ↔ `pending` ↔ `sold`).
  - Order placement and completion (which can move pets to `sold`, inferred).

---

### User

Represents a user account in the system, covering both customers and staff. Used for authentication (login/logout) and profile management.

| Field      | Type            | Required | Description |
|------------|-----------------|----------|-------------|
| id         | integer (int64) | No       | Unique identifier for the user. Typically assigned by the system. |
| username   | string          | No       | Unique username used for login and user lookup. |
| firstName  | string          | No       | User’s given name. |
| lastName   | string          | No       | User’s family name. |
| email      | string          | No       | User’s email address. |
| password   | string          | No       | User’s password in clear text (for request payloads). Should be handled securely in actual implementations. |
| phone      | string          | No       | Contact phone number. |
| userStatus | integer (int32) | No       | Status code indicating user’s account state (e.g., 0 = inactive, 1 = active – specific mapping inferred). |

**Validation rules**:
- `id`:
  - If provided, must be a positive 64-bit integer (inferred).
- `username`:
  - If used for creation, should be unique (inferred).
  - When used in path operations, must match an existing username.
- `email`:
  - If provided, must be a syntactically valid email address (inferred).
- `password`:
  - If provided, must be non-empty; minimum length constraints likely (e.g., ≥ 5 chars, inferred).
- `userStatus`:
  - If provided, must be a 32-bit integer. Specific semantic values are implementation-defined.

**State transitions** (userStatus – inferred):
- `inactive` (e.g., 0) → `active` (e.g., 1) upon successful onboarding.
- `active` → `inactive` or other codes for suspension/closure.
- Delete operations represent a terminal removal rather than another status value.

---

### ApiResponse

Represents a generic API operation response used primarily by the image upload endpoint to convey results and messages.

| Field   | Type            | Required | Description |
|---------|-----------------|----------|-------------|
| code    | integer (int32) | No       | Response status or business code associated with the operation. |
| type    | string          | No       | Short, categorised type or key for the response (e.g., “success”, “error” – inferred). |
| message | string          | No       | Human-readable message describing the result. |

**Validation rules**:
- `code`:
  - If provided, must be a 32-bit integer.
- `type`:
  - If provided, must be a non-empty string (inferred).
- `message`:
  - If provided, should be a descriptive string (inferred).

---

### PetUploadImageRequest

Represents the payload and parameters required to upload an image for a specific pet.

| Field              | Type              | Required | Description |
|--------------------|-------------------|----------|-------------|
| petId              | integer (int64)   | Yes      | ID of the pet whose image is being uploaded. Must reference an existing `Pet`. |
| additionalMetadata | string            | No       | Free-form metadata describing the image (e.g., photographer, angle, notes). |
| file               | binary (octet-stream) | Yes  | Binary image content in `application/octet-stream` format. |

**Validation rules**:
- `petId`:
  - Must be a positive 64-bit integer.
  - Must reference an existing pet, otherwise `404 Pet not found`.
- `file`:
  - Required.
  - Must contain non-empty binary content.
  - Image type or size limits may be enforced by implementation (inferred).
- `additionalMetadata`:
  - Optional; any string allowed (inferred).

**State transitions**:
- On successful upload, the pet’s associated media set is extended (relationship is implicit; not stored as a field on `Pet` in the schema but typically linked to `photoUrls`, inferred).

---

### PetSearchByStatusRequest

Represents the query parameters for searching pets by status.

| Field  | Type   | Required | Description |
|--------|--------|----------|-------------|
| status | string | Yes      | Pet status filter; one of `available`, `pending`, `sold`. Multiple values can be provided as comma-separated strings. |

**Validation rules**:
- `status`:
  - Required.
  - Comma-separated string; each token must be one of: `available`, `pending`, `sold`.
  - Invalid values yield `400 Invalid status value`.

---

### PetSearchByTagsRequest

Represents the query parameters for searching pets by tags.

| Field | Type      | Required | Description |
|-------|-----------|----------|-------------|
| tags  | string[]  | Yes      | List of tag names to filter by. Provided as a query parameter that can be repeated or comma-separated. |

**Validation rules**:
- `tags`:
  - Must contain at least one value.
  - Each tag must be a non-empty string.
  - Invalid tags result in `400 Invalid tag value`.

---

### PetUpdateWithFormRequest

Represents the parameters for updating a pet using form-style inputs (via query/form-encoded fields).

| Field | Type            | Required | Description |
|-------|-----------------|----------|-------------|
| petId | integer (int64) | Yes      | ID of the pet that needs to be updated. |
| name  | string          | No       | New name of the pet. |
| status| string          | No       | New status of the pet (string; typical values: `available`, `pending`, `sold` – inferred). |

**Validation rules**:
- `petId`:
  - Required and must be a positive 64-bit integer.
- `name`:
  - If provided, must be non-empty.
- `status`:
  - If provided, should be one of: `available`, `pending`, `sold` (inferred).
- At least one of `name` or `status` should be provided; otherwise the update is a no-op (inferred).

**State transitions**:
- Updates the underlying `Pet` resource, potentially changing its `name` and/or `status` as per `Pet` state transitions.

---

### OrderCreateRequest

Represents the request body used to place an order for a pet.

| Field    | Type              | Required | Description |
|----------|-------------------|----------|-------------|
| id       | integer (int64)   | No       | Order identifier; usually assigned by the system (client-provided ID may be accepted, inferred). |
| petId    | integer (int64)   | No       | The pet to be ordered. Should reference an existing `Pet`. |
| quantity | integer (int32)   | No       | Quantity to order. |
| shipDate | string (date-time)| No       | Desired or planned shipping date/time. |
| status   | string (enum)     | No       | Initial order status. Typically `placed` on creation (inferred). |
| complete | boolean           | No       | Initial completion flag; typically `false` on creation (inferred). |

**Validation rules**:
- Same as `Order`.
- `petId` is logically required to place a meaningful order, though not marked required in schema (business rule inferred).
- `quantity` should default to `1` if omitted (inferred for a pet store).

**State transitions**:
- On successful creation (`placeOrder`), a new `Order` moves into `placed` status.

---

### OrderDeleteRequest

Represents parameters needed to delete an existing order.

| Field   | Type            | Required | Description |
|---------|-----------------|----------|-------------|
| orderId | integer (int64) | Yes      | ID of the order that needs to be deleted. |

**Validation rules**:
- `orderId`:
  - Required.
  - Must be a positive 64-bit integer.
  - For demo behavior: IDs `< 1000` succeed; `>= 1000` or non-integers trigger API errors (per description).

**State transitions**:
- Deleting an order transitions it from any status to a terminal “deleted” state, represented by absence of the resource.

---

### UserCreateRequest

Represents the request body used to create a single user.

| Field      | Type            | Required | Description |
|------------|-----------------|----------|-------------|
| id         | integer (int64) | No       | System-wide user identifier. |
| username   | string          | No       | Unique login name for the user. Recommended required for login. |
| firstName  | string          | No       | First name. |
| lastName   | string          | No       | Last name. |
| email      | string          | No       | Email address. |
| password   | string          | No       | Password in clear text (for input). |
| phone      | string          | No       | Phone number. |
| userStatus | integer (int32) | No       | Numeric status code for the user account. |

**Validation rules**:
- Same as `User`.
- Business-level (inferred):
  - `username`, `email`, `password` are typically required for functional accounts even though not marked required in the schema.

**State transitions**:
- On creation, user typically enters an “active” state (e.g., `userStatus=1`, inferred).

---

### UserBulkCreateRequest

Represents the request payload for creating multiple users at once.

| Field        | Type    | Required | Description |
|--------------|---------|----------|-------------|
| users        | User[]  | Yes      | Array of `User` objects to be created. Each entry follows the `User` model. |

**Validation rules**:
- `users`:
  - Must be an array with at least one element.
  - Each user must satisfy `UserCreateRequest` validation.
  - Failures may be per-item or all-or-nothing depending on implementation (inferred).

**State transitions**:
- Bulk operation creates multiple user accounts in one call.

---

### UserLoginRequest

Represents query parameters for logging a user into the system.

| Field    | Type   | Required | Description |
|----------|--------|----------|-------------|
| username | string | No       | Username for login. |
| password | string | No       | Password for login in clear text. |

**Validation rules**:
- `username` and `password`:
  - Both should be provided together; missing one yields `400 Invalid username/password supplied` (business rule inferred).
- Successful login:
  - Returns a token string with headers:
    - `X-Rate-Limit` (int32): Allowed calls per hour.
    - `X-Expires-After` (date-time): Token expiry timestamp.

**State transitions**:
- Successful login establishes a logged-in session or token (represented externally, not in this data model).

---

### UserLogoutRequest

Represents the absence of parameters required for logout.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| (none)| —    | —        | Logout requires no input parameters. |

**Validation rules**:
- None at the payload level; relies on authentication context (inferred).

**State transitions**:
- Terminates the current user session or token.

---

### UserPathRequest

Represents the path parameter used for user-specific operations.

| Field    | Type   | Required | Description |
|----------|--------|----------|-------------|
| username | string | Yes      | Username of the user targeted by get, update, or delete operations. |

**Validation rules**:
- `username`:
  - Required.
  - Must match an existing user for successful GET/PUT/DELETE, otherwise `404 User not found`.

**State transitions**:
- Used to read, modify, or delete the underlying `User` entity.

---

### PetIdPathRequest

Represents the path parameter used for pet-specific operations.

| Field | Type            | Required | Description |
|-------|-----------------|----------|-------------|
| petId | integer (int64) | Yes      | ID of the pet targeted by operations such as get, update with form, delete, and upload image. |

**Validation rules**:
- `petId`:
  - Required.
  - Must be a positive 64-bit integer.
  - Must reference an existing pet for non-create operations.

---

### OrderIdPathRequest

Represents the path parameter used for order-specific read/delete operations.

| Field   | Type            | Required | Description |
|---------|-----------------|----------|-------------|
| orderId | integer (int64) | Yes      | ID of the order to fetch or delete. |

**Validation rules**:
- `orderId`:
  - Required and must be a positive 64-bit integer.
  - For GET:
    - Description indicates special demo behavior: valid responses for IDs `<= 5` or `> 10`; others may generate exceptions.
  - For DELETE:
    - Valid IDs are `< 1000`; others produce API errors.

---

### SecurityCredentials (inferred)

Represents authentication and authorization tokens or keys used by the API.

| Field        | Type   | Required | Description |
|--------------|--------|----------|-------------|
| api_key      | string | No       | API key used in the `api_key` header for certain operations (e.g., get inventory, get/delete pet). |
| oauth_token  | string | No       | OAuth 2.0 token obtained via the `petstore_auth` implicit flow. Used to authorize pet-related operations. |

**Validation rules**:
- `api_key`:
  - If provided, must be a non-empty string.
- `oauth_token`:
  - Must be a valid bearer token obtained via configured OAuth flow (inferred).

**State transitions**:
- Tokens expire per `X-Expires-After` in login responses or OAuth server policies.

---

## Configuration Files

Below are example configurations showing how an application might represent and use these entities and related settings.

### Example: Application Configuration (YAML)

```yaml
petstore:
  baseUrl: https://petstore3.swagger.io/api/v3

  auth:
    # Option 1: API key for operations that support `api_key` security scheme
    apiKey: "your-api-key-value"

    # Option 2: OAuth2 implicit flow token for `petstore_auth`
    oauthToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

  defaults:
    # Default search filters (inferred usage)
    petStatusFilters:
      - available
      - pending

    # Default order settings
    order:
      defaultQuantity: 1
      autoCompleteOnDelivered: true

  # Example initial data payloads
  seedData:
    categories:
      - id: 1
        name: Dogs
      - id: 2
        name: Cats

    pets:
      - id: 10
        name: doggie
        category:
          id: 1
          name: Dogs
        photoUrls:
          - https://cdn.example.com/pets/10-1.jpg
        tags:
          - id: 100
            name: puppy
        status: available

    users:
      - id: 10
        username: theUser
        firstName: John
        lastName: James
        email: john@email.com
        password: "12345"
        phone: "12345"
        userStatus: 1

    orders:
      - id: 50
        petId: 10
        quantity: 1
        shipDate: 2026-03-12T10:00:00Z
        status: placed
        complete: false
```

### Example: Environment Variables (.env)

```env
PETSTORE_BASE_URL=https://petstore3.swagger.io/api/v3

# Security
PETSTORE_API_KEY=your-api-key-value
PETSTORE_OAUTH_TOKEN=your-oauth-access-token

# Default filters (comma-separated)
PETSTORE_DEFAULT_PET_STATUS=available,pending

# Behavior flags
PETSTORE_AUTO_COMPLETE_ORDERS=true
PETSTORE_DEFAULT_ORDER_QUANTITY=1
```

### Example: Pet Creation Payload (JSON)

```json
{
  "id": 10,
  "name": "doggie",
  "category": {
    "id": 1,
    "name": "Dogs"
  },
  "photoUrls": [
    "https://cdn.example.com/pets/doggie-main.jpg"
  ],
  "tags": [
    {
      "id": 101,
      "name": "puppy"
    },
    {
      "id": 102,
      "name": "small"
    }
  ],
  "status": "available"
}
```

### Example: Order Placement Payload (JSON)

```json
{
  "petId": 10,
  "quantity": 1,
  "shipDate": "2026-03-12T10:00:00Z",
  "status": "placed",
  "complete": false
}
```

### Example: User Bulk Creation Payload (JSON)

```json
[
  {
    "id": 10,
    "username": "theUser",
    "firstName": "John",
    "lastName": "James",
    "email": "john@email.com",
    "password": "12345",
    "phone": "12345",
    "userStatus": 1
  },
  {
    "id": 11,
    "username": "staffAdmin",
    "firstName": "Alice",
    "lastName": "Admin",
    "email": "alice.admin@example.com",
    "password": "SecureP@ssw0rd",
    "phone": "+1-555-0100",
    "userStatus": 1
  }
]
```

### Example: Inventory Snapshot Response (JSON)

```json
{
  "available": 12,
  "pending": 3,
  "sold": 27
}
```

### Example: Image Upload Request (curl)

```bash
curl -X POST "https://petstore3.swagger.io/api/v3/pet/10/uploadImage?additionalMetadata=front+view" \
  -H "Authorization: Bearer ${PETSTORE_OAUTH_TOKEN}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@doggie-front.jpg"
```

### Example: Login Response (JSON + Headers)

```http
HTTP/1.1 200 OK
X-Rate-Limit: 1000
X-Expires-After: 2026-03-12T10:00:00Z
Content-Type: application/json

"session-token-or-message"
```

---

## Relationships

```text
Pet           ──1:1──▶  Category
  A pet belongs to zero or one category (e.g., "Dogs").

Pet           ──1:N──▶  Tag
  A pet can have multiple tags; a tag can be reused across many pets (many-to-many overall, represented via Pet.tags).

Order         ──N:1──▶  Pet
  Each order references a single pet via petId; a pet can appear in many orders over time.

InventorySnapshot ──aggregates──▶ Pet
  Inventory snapshot is a derived, aggregated view over all pets, grouped by Pet.status.

UserLoginRequest ──authenticates──▶ User
  Login uses username/password to authenticate and establish a session for a user.

UserBulkCreateRequest ──1:N──▶ User
  Bulk creation wraps multiple User entities into a single operation.

PetUploadImageRequest ──N:1──▶ Pet
  Image uploads are associated with a single pet via petId; a pet can have multiple uploaded images.

OrderIdPathRequest ──identifies──▶ Order
  Path-based orderId is the handle for retrieving or deleting a specific order.

PetIdPathRequest ──identifies──▶ Pet
  Path-based petId is the handle for get, update, delete, and image upload operations.

UserPathRequest ──identifies──▶ User
  Path-based username is used to get, update, and delete a user.

SecurityCredentials (api_key / oauth_token) ──authorizes──▶ Pet / Order / User operations
  Security credentials gate access to operations according to the configured security schemes.
```