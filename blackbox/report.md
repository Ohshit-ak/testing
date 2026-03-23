# Black Box Testing — Bug Report
## QuickCart REST API

---

## Endpoint: `GET /api/v1/profile`

### Bug 1 — Missing X-User-ID returns 404 instead of 400

**Request**
- Method: GET
- URL: `http://localhost:8080/api/v1/profile`
- Headers: `X-Roll-Number: 2024111004` (X-User-ID omitted)
- Body: none

**Expected Result:** `400 Bad Request` (missing required header)

**Actual Result:** `404 Not Found`

---

## Endpoint: `PUT /api/v1/profile`

### Bug 2 — Phone number with non-digit characters is accepted

**Request**
- Method: PUT
- URL: `http://localhost:8080/api/v1/profile`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"name": "Alice", "phone": "98765-3210"}`

**Expected Result:** `400 Bad Request` (phone must be exactly 10 digits, no other characters)

**Actual Result:** `200 OK` — profile updated with invalid phone number

---

### Bug 3 — Missing X-User-ID returns 404 instead of 400

**Request**
- Method: PUT
- URL: `http://localhost:8080/api/v1/profile`
- Headers: `X-Roll-Number: 2024111004` (X-User-ID omitted)
- Body: `{"name": "Alice", "phone": "9876543210"}`

**Expected Result:** `400 Bad Request`

**Actual Result:** `404 Not Found`

---

## Endpoint: `GET /api/v1/products`

### Bug 4 — Price field does not match the database value for some products

**Request**
- Method: GET
- URL: `http://localhost:8080/api/v1/products`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: none

**Expected Result:** Each product's `price` field must exactly match the value stored in the database (verifiable via `GET /api/v1/admin/products`)

**Actual Result:** The `price` field for some products returns a different value than what is stored in the database

---

## Endpoint: `GET /api/v1/products/{product_id}`

### Bug 5 — Fetching an inactive product by ID returns 200 instead of 404

**Request**
- Method: GET
- URL: `http://localhost:8080/api/v1/products/3` (where product 3 is inactive)
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: none

**Expected Result:** `404 Not Found` (inactive products should not be accessible)

**Actual Result:** `200 OK` with the full product details

---

### Bug 6 — Missing X-User-ID returns 404 instead of 400

**Request**
- Method: GET
- URL: `http://localhost:8080/api/v1/products/1`
- Headers: `X-Roll-Number: 2024111004` (X-User-ID omitted)
- Body: none

**Expected Result:** `400 Bad Request`

**Actual Result:** `404 Not Found`

---

### Bug 7 — Non-existent X-User-ID returns 404 instead of 400

**Request**
- Method: GET
- URL: `http://localhost:8080/api/v1/products/1`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 99999`
- Body: none

**Expected Result:** `400 Bad Request` (user does not exist)

**Actual Result:** `404 Not Found`

---

## Endpoint: `POST /api/v1/cart/add`

### Bug 8 — Adding quantity 0 is accepted instead of rejected

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/cart/add`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"product_id": 1, "quantity": 0}`

**Expected Result:** `400 Bad Request` (quantity must be at least 1)

**Actual Result:** `200 OK` — item added with quantity 0

---

### Bug 9 — Adding the same product twice replaces quantity instead of accumulating

**Request (Step 1)**
- Method: POST
- URL: `http://localhost:8080/api/v1/cart/add`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"product_id": 1, "quantity": 2}`

**Request (Step 2)**
- Method: POST
- URL: `http://localhost:8080/api/v1/cart/add`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"product_id": 1, "quantity": 3}`

**Expected Result:** Cart item for product 1 should have quantity 5 (2 + 3)

**Actual Result:** Cart item for product 1 has quantity 3 (second value replaces the first)

---

### Bug 10 — Cart total does not include the last item

**Request**
- Method: GET
- URL: `http://localhost:8080/api/v1/cart`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: none

**Expected Result:** `total` equals the sum of all item subtotals including the last one

**Actual Result:** The last item's subtotal is excluded from the cart total

---

## Endpoint: `POST /api/v1/cart/remove`

### Bug 11 — Removing a product not in the cart returns 200 instead of 404

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/cart/remove`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"product_id": 999999}`

**Expected Result:** `404 Not Found` (product is not in the cart)

**Actual Result:** `200 OK`

---

## Endpoint: `POST /api/v1/coupon/apply`

### Bug 12 — Expired coupon is accepted instead of rejected

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/coupon/apply`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"coupon_code": "EXPIRED10"}`

**Expected Result:** `400 Bad Request` (coupon is expired)

**Actual Result:** `200 OK` — discount applied using an expired coupon

---

### Bug 13 — PERCENT coupon discount exceeds the maximum cap

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/coupon/apply`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"coupon_code": "SAVE20"}` (20% off, max discount = 100)

**Expected Result:** Discount capped at 100 when calculated percentage exceeds it

**Actual Result:** Discount applied as raw percentage with no cap enforced

---

## Endpoint: `POST /api/v1/checkout`

### Bug 14 — COD order above 5000 is accepted instead of rejected

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/checkout`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"payment_method": "COD"}` (cart total = 5500)

**Expected Result:** `400 Bad Request` (COD not allowed above 5000)

**Actual Result:** `200 OK` — COD order placed with total above the limit

---

### Bug 15 — GST applied more than once on some orders

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/checkout`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"payment_method": "CARD"}` (cart subtotal = 200)

**Expected Result:** `total_amount = 210.00` (200 × 1.05, GST applied once)

**Actual Result:** `total_amount = 220.50` (GST applied twice)

---

## Endpoint: `POST /api/v1/wallet/add`

### Bug 16 — Adding amount 0 is accepted instead of rejected

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/wallet/add`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"amount": 0}`

**Expected Result:** `400 Bad Request` (amount must be more than 0)

**Actual Result:** `200 OK`

---

### Bug 17 — Adding amount above 100000 is accepted instead of rejected

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/wallet/add`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"amount": 100001}`

**Expected Result:** `400 Bad Request` (max allowed is 100000)

**Actual Result:** `200 OK` — balance topped up with amount exceeding the limit

---

## Endpoint: `POST /api/v1/wallet/pay`

### Bug 18 — Paying more than wallet balance is accepted instead of rejected

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/wallet/pay`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"amount": 99999}` (wallet balance = 50)

**Expected Result:** `400 Bad Request` (insufficient balance)

**Actual Result:** `200 OK` — payment deducted, balance goes negative

---

## Endpoint: `POST /api/v1/orders/{order_id}/cancel`

### Bug 19 — Cancelling a delivered order returns 200 instead of 400

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/orders/7/cancel` (order 7 has status DELIVERED)
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: none

**Expected Result:** `400 Bad Request` (delivered orders cannot be cancelled)

**Actual Result:** `200 OK` — order status changed despite being delivered

---

### Bug 20 — Stock is not restored after order cancellation

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/orders/5/cancel`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: none

**Expected Result:** After cancellation, each product's stock in the order increases by the ordered quantity

**Actual Result:** Product stock remains unchanged after cancellation

---

## Endpoint: `GET /api/v1/orders/{order_id}/invoice`

### Bug 21 — Invoice total does not match the actual order total

**Request**
- Method: GET
- URL: `http://localhost:8080/api/v1/orders/2/invoice`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: none

**Expected Result:** `invoice.total` equals `order.total_amount` exactly

**Actual Result:** `invoice.total` shows a different value than the stored order total

---

## Endpoint: `POST /api/v1/products/{product_id}/reviews`

### Bug 22 — Rating of 0 is accepted instead of rejected

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/products/1/reviews`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"rating": 0, "comment": "Bad"}`

**Expected Result:** `400 Bad Request` (rating must be between 1 and 5)

**Actual Result:** `200 OK` — review saved with rating 0

---

### Bug 23 — Average rating is returned as an integer floor instead of a decimal

**Request**
- Method: GET
- URL: `http://localhost:8080/api/v1/products/1/reviews`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: none

**Expected Result:** If ratings are 3 and 4, `average_rating` should be `3.5`

**Actual Result:** `average_rating` returns `3` (integer floor instead of proper decimal)

---

## Endpoint: `PUT /api/v1/support/tickets/{ticket_id}`

### Bug 24 — Status can jump directly from OPEN to CLOSED

**Request**
- Method: PUT
- URL: `http://localhost:8080/api/v1/support/tickets/1`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"status": "CLOSED"}` (current status is OPEN)

**Expected Result:** `400 Bad Request` (OPEN can only transition to IN_PROGRESS)

**Actual Result:** `200 OK` — ticket status set to CLOSED directly from OPEN

---

### Bug 25 — A closed ticket can be re-opened

**Request**
- Method: PUT
- URL: `http://localhost:8080/api/v1/support/tickets/1`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"status": "OPEN"}` (current status is CLOSED)

**Expected Result:** `400 Bad Request` (status transitions are one-directional; CLOSED is terminal)

**Actual Result:** `200 OK` — closed ticket moved back to OPEN

---

## Endpoint: `POST /api/v1/addresses`

### Bug 26 — Adding a new default address does not unset the previous default

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/addresses`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"label": "OFFICE", "street": "10 Main Street", "city": "Hyderabad", "pincode": "500001", "is_default": true}`
  (Another address already exists with `is_default: true`)

**Expected Result:** The previously default address has `is_default` set to false; only one address is default at a time

**Actual Result:** Both the old and new addresses have `is_default: true`

---

## Endpoint: `PUT /api/v1/addresses/{address_id}`

### Bug 27 — Response still shows old data after update

**Request**
- Method: PUT
- URL: `http://localhost:8080/api/v1/addresses/1`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"street": "999 New Street Name"}`

**Expected Result:** Response body contains the updated street `"999 New Street Name"`

**Actual Result:** Response body still shows the old street value before the update

---

## Endpoint: `POST /api/v1/loyalty/redeem`

### Bug 28 — Redeeming 0 points is accepted instead of rejected

**Request**
- Method: POST
- URL: `http://localhost:8080/api/v1/loyalty/redeem`
- Headers: `X-Roll-Number: 2024111004`, `X-User-ID: 1`
- Body: `{"amount": 0}`

**Expected Result:** `400 Bad Request` (the amount to redeem must be at least 1)

**Actual Result:** `200 OK` — redemption processed with amount 0