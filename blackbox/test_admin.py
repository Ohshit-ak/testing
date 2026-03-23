import requests

BASE_URL = "http://localhost:8080/api/v1"
ROLL_NUMBER = "2024111004"  # Replace with your actual roll number

# Base headers for all requests (no X-User-ID needed for admin endpoints)
ADMIN_HEADERS = {
    "X-Roll-Number": ROLL_NUMBER
}

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

def check(test_name, condition, actual=None):
    if condition:
        print(f"  [{PASS}] {test_name}")
    else:
        print(f"  [{FAIL}] {test_name} | Got: {actual}")

def run_test(name, fn):
    print(f"\n{'='*55}")
    print(f" {name}")
    print(f"{'='*55}")
    fn()

# ─────────────────────────────────────────────
# MISSING / INVALID X-Roll-Number HEADER TESTS
# ─────────────────────────────────────────────
def test_missing_roll_number():
    endpoints = [
        "/admin/users",
        "/admin/carts",
        "/admin/orders",
        "/admin/products",
        "/admin/coupons",
        "/admin/tickets",
        "/admin/addresses",
    ]
    for ep in endpoints:
        r = requests.get(f"{BASE_URL}{ep}")  # No headers at all
        check(f"Missing X-Roll-Number on {ep} → 401", r.status_code == 401, r.status_code)

def test_invalid_roll_number():
    bad_headers = {"X-Roll-Number": "abc"}
    endpoints = [
        "/admin/users",
        "/admin/carts",
        "/admin/orders",
        "/admin/products",
        "/admin/coupons",
        "/admin/tickets",
        "/admin/addresses",
    ]
    for ep in endpoints:
        r = requests.get(f"{BASE_URL}{ep}", headers=bad_headers)
        check(f"Invalid X-Roll-Number on {ep} → 400", r.status_code == 400, r.status_code)

# ─────────────────────────────────────────────
# GET /admin/users
# ─────────────────────────────────────────────
def test_admin_users():
    r = requests.get(f"{BASE_URL}/admin/users", headers=ADMIN_HEADERS)
    check("Status 200", r.status_code == 200, r.status_code)

    data = r.json()
    check("Response is a list", isinstance(data, list), type(data))

    if data:
        user = data[0]
        check("Each user has 'user_id'", "user_id" in user, user)
        check("Each user has 'name'", "name" in user, user)
        check("Each user has 'wallet_balance'", "wallet_balance" in user, user)
        check("Each user has 'loyalty_points'", "loyalty_points" in user, user)

# ─────────────────────────────────────────────
# GET /admin/users/{user_id}
# ─────────────────────────────────────────────
def test_admin_user_by_id():
    # First get all users to find a valid ID
    r_all = requests.get(f"{BASE_URL}/admin/users", headers=ADMIN_HEADERS)
    users = r_all.json()

    if users:
        valid_id = users[0]["user_id"]
        r = requests.get(f"{BASE_URL}/admin/users/{valid_id}", headers=ADMIN_HEADERS)
        check(f"Status 200 for user {valid_id}", r.status_code == 200, r.status_code)

        user = r.json()
        check("Has correct 'user_id'", user.get("user_id") == valid_id, user.get("user_id"))
        check("Has 'name'", "name" in user, user)
        check("Has 'wallet_balance'", "wallet_balance" in user, user)
        check("Has 'loyalty_points'", "loyalty_points" in user, user)
    else:
        print("  [SKIP] No users found to test")

    # Test non-existent user
    r404 = requests.get(f"{BASE_URL}/admin/users/999999", headers=ADMIN_HEADERS)
    check("Non-existent user → 404", r404.status_code == 404, r404.status_code)

# ─────────────────────────────────────────────
# GET /admin/carts
# ─────────────────────────────────────────────
def test_admin_carts():
    r = requests.get(f"{BASE_URL}/admin/carts", headers=ADMIN_HEADERS)
    check("Status 200", r.status_code == 200, r.status_code)

    data = r.json()
    check("Response is a list", isinstance(data, list), type(data))

    if data:
        cart = data[0]
        check("Cart has 'user_id'", "user_id" in cart, cart)
        check("Cart has 'items'", "items" in cart, cart)
        check("Cart has 'total'", "total" in cart, cart)

        if cart["items"]:
            item = cart["items"][0]
            check("Item has 'product_id'", "product_id" in item, item)
            check("Item has 'quantity'", "quantity" in item, item)
            check("Item has 'subtotal'", "subtotal" in item, item)

            # Verify subtotal = quantity * unit_price (if unit_price present)
            if "unit_price" in item:
                expected = round(item["quantity"] * item["unit_price"], 2)
                actual = round(item["subtotal"], 2)
                check(
                    f"Subtotal = qty × unit_price ({expected})",
                    abs(expected - actual) < 0.01,
                    actual
                )

# ─────────────────────────────────────────────
# GET /admin/orders
# ─────────────────────────────────────────────
def test_admin_orders():
    r = requests.get(f"{BASE_URL}/admin/orders", headers=ADMIN_HEADERS)
    check("Status 200", r.status_code == 200, r.status_code)

    data = r.json()
    check("Response is a list", isinstance(data, list), type(data))

    if data:
        order = data[0]
        check("Order has 'order_id'", "order_id" in order, order)
        check("Order has 'user_id'", "user_id" in order, order)
        check("Order has 'total_amount'", "total_amount" in order, order)
        check("Order has 'gst_amount'", "gst_amount" in order, order)
        check("Order has 'payment_status'", "payment_status" in order, order)
        check("Order has 'payment_method'", "payment_method" in order, order)
        check("Order has 'order_status'", "order_status" in order, order)
        valid_payement_methods = {"COD", "CARD", "WALLET", "UPI"}
        check(
            "payment_method is valid",
            order["payment_method"] in valid_payement_methods,
            order["payment_method"]
        )
        valid_payment_statuses = {"PENDING", "PAID", "FAILED"}
        check(
            "payment_status is valid",
            order["payment_status"] in valid_payment_statuses,
            order["payment_status"]
        )

        valid_order_statuses = {"PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"}
        check(
            "order_status is valid",
            order["order_status"] in valid_order_statuses,
            order["order_status"]
        )

# ─────────────────────────────────────────────
# GET /admin/products
# ─────────────────────────────────────────────
def test_admin_products():
    r = requests.get(f"{BASE_URL}/admin/products", headers=ADMIN_HEADERS)
    check("Status 200", r.status_code == 200, r.status_code)

    data = r.json()
    check("Response is a list", isinstance(data, list), type(data))

    if data:
        product = data[0]
        check("Product has 'product_id'", "product_id" in product, product)
        check("Product has 'name'", "name" in product, product)
        check("Product has 'price'", "price" in product, product)
        check("Product has 'is_active'", "is_active" in product, product)

        # Admin endpoint should include inactive products too
        has_inactive = any(not p.get("is_active", True) for p in data)
        print(f"  [INFO] Inactive products present: {has_inactive}")

# ─────────────────────────────────────────────
# GET /admin/coupons
# ─────────────────────────────────────────────
def test_admin_coupons():
    r = requests.get(f"{BASE_URL}/admin/coupons", headers=ADMIN_HEADERS)
    check("Status 200", r.status_code == 200, r.status_code)

    data = r.json()
    check("Response is a list", isinstance(data, list), type(data))

    if data:
        coupon = data[0]
        check("Coupon has 'coupon_code'", "coupon_code" in coupon, coupon)
        check("Coupon has 'discount_type'", "discount_type" in coupon, coupon)
        check("Coupon has 'discount_value'", "discount_value" in coupon, coupon)

        valid_types = {"PERCENT", "FIXED"}
        check(
            "discount_type is PERCENT or FIXED",
            coupon["discount_type"] in valid_types,
            coupon["discount_type"]
        )

# ─────────────────────────────────────────────
# GET /admin/tickets
# ─────────────────────────────────────────────
def test_admin_tickets():
    r = requests.get(f"{BASE_URL}/admin/tickets", headers=ADMIN_HEADERS)
    check("Status 200", r.status_code == 200, r.status_code)

    data = r.json()
    check("Response is a list", isinstance(data, list), type(data))

    if data:
        ticket = data[0]
        check("Ticket has 'ticket_id'", "ticket_id" in ticket, ticket)
        check("Ticket has 'user_id'", "user_id" in ticket, ticket)
        check("Ticket has 'subject'", "subject" in ticket, ticket)
        check("Ticket has 'message'", "message" in ticket, ticket)
        check("Ticket has 'status'", "status" in ticket, ticket)

        valid_statuses = {"OPEN", "IN_PROGRESS", "CLOSED"}
        check(
            "status is valid",
            ticket["status"] in valid_statuses,
            ticket["status"]
        )

# ─────────────────────────────────────────────
# GET /admin/addresses
# ─────────────────────────────────────────────
def test_admin_addresses():
    r = requests.get(f"{BASE_URL}/admin/addresses", headers=ADMIN_HEADERS)
    check("Status 200", r.status_code == 200, r.status_code)

    data = r.json()
    check("Response is a list", isinstance(data, list), type(data))

    if data:
        address = data[0]
        check("Address has 'address_id'", "address_id" in address, address)
        check("Address has 'user_id'", "user_id" in address, address)
        check("Address has 'label'", "label" in address, address)
        check("Address has 'street'", "street" in address, address)
        check("Address has 'city'", "city" in address, address)
        check("Address has 'pincode'", "pincode" in address, address)
        check("Address has 'is_default'", "is_default" in address, address)

        valid_labels = {"HOME", "OFFICE", "OTHER"}
        check(
            "label is HOME / OFFICE / OTHER",
            address["label"] in valid_labels,
            address["label"]
        )

        check(
            "pincode is 6 digits",
            len(str(address["pincode"])) == 6,
            address["pincode"]
        )

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    run_test("Missing X-Roll-Number Header (All Admin Endpoints)", test_missing_roll_number)
    run_test("Invalid X-Roll-Number Header (All Admin Endpoints)", test_invalid_roll_number)
    run_test("GET /admin/users", test_admin_users)
    run_test("GET /admin/users/{user_id}", test_admin_user_by_id)
    run_test("GET /admin/carts", test_admin_carts)
    run_test("GET /admin/orders", test_admin_orders)
    run_test("GET /admin/products", test_admin_products)
    run_test("GET /admin/coupons", test_admin_coupons)
    run_test("GET /admin/tickets", test_admin_tickets)
    run_test("GET /admin/addresses", test_admin_addresses)

    print(f"\n{'='*55}")
    print(" All admin tests complete.")
    print(f"{'='*55}\n")