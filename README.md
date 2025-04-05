# E-commerce API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication

### Register
```http
POST /auth/register/
```
Request body:
```json
{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

### Login
```http
POST /auth/login/
```
Request body:
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```
Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Token
```http
POST /auth/refresh/
```
Request body:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Get Profile
```http
GET /auth/profile/
```
Headers:
```
Authorization: Bearer <access_token>
```

### Update Profile
```http
PUT /auth/update-profile/
```
Headers:
```
Authorization: Bearer <access_token>
```
Request body:
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "user@example.com"
}
```

### Change Password
```http
POST /auth/change-password/
```
Headers:
```
Authorization: Bearer <access_token>
```
Request body:
```json
{
    "old_password": "oldpassword123",
    "new_password": "newpassword123"
}
```

## Products

### List Products
```http
GET /products/
```
Query parameters:
- `search`: Search by name or description
- `min_price`: Minimum price
- `max_price`: Maximum price
- `category`: Filter by category slug
- `in_stock`: Filter by stock availability

### Get Product
```http
GET /products/{id}/
```

### Create Product (Admin only)
```http
POST /products/
```
Headers:
```
Authorization: Bearer <access_token>
```
Request body:
```json
{
    "name": "Product Name",
    "description": "Product Description",
    "price": 99.99,
    "category": "category-slug",
    "stock": 100,
    "images": [file1, file2]
}
```

## Categories

### List Categories
```http
GET /categories/
```

### Get Category
```http
GET /categories/{slug}/
```

### Create Category (Admin only)
```http
POST /categories/
```
Headers:
```
Authorization: Bearer <access_token>
```
Request body:
```json
{
    "name": "Category Name",
    "description": "Category Description",
    "parent": "parent-category-slug"
}
```

## Cart

### Get Cart
```http
GET /carts/
```
Headers:
```
Authorization: Bearer <access_token>
```

### Add Item to Cart
```http
POST /carts/add-item/
```
Headers:
```
Authorization: Bearer <access_token>
```
Request body:
```json
{
    "product_id": "product-id",
    "quantity": 2
}
```

### Update Item Quantity
```http
POST /carts/update-quantity/
```
Headers:
```
Authorization: Bearer <access_token>
```
Request body:
```json
{
    "product_id": "product-id",
    "quantity": 3
}
```

### Apply Discount
```http
POST /carts/apply-discount/
```
Headers:
```
Authorization: Bearer <access_token>
```
Request body:
```json
{
    "discount_code": "DISCOUNT20"
}
```

## Orders

### Create Order
```http
POST /orders/
```
Headers:
```
Authorization: Bearer <access_token>
```
Request body:
```json
{
    "shipping_address": {
        "street": "123 Main St",
        "city": "City",
        "state": "State",
        "zip_code": "12345",
        "country": "Country"
    },
    "billing_address": {
        "street": "123 Main St",
        "city": "City",
        "state": "State",
        "zip_code": "12345",
        "country": "Country"
    },
    "phone_number": "+1234567890",
    "email": "user@example.com",
    "items": [
        {
            "product_id": "product-id",
            "quantity": 2
        }
    ],
    "discount_code": "DISCOUNT20"
}
```

### Get Order
```http
GET /orders/{id}/
```
Headers:
```
Authorization: Bearer <access_token>
```

### List User Orders
```http
GET /orders/my-orders/
```
Headers:
```
Authorization: Bearer <access_token>
```

## Error Responses

### 400 Bad Request
```json
{
    "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

## Rate Limiting
- Authentication endpoints: 5 requests per minute
- Other endpoints: 100 requests per minute 