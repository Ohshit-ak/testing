"""
QuickCart — Support Tickets Section Tests
Endpoints:
  POST /api/v1/support/ticket
  GET  /api/v1/support/tickets
  PUT  /api/v1/support/tickets/{ticket_id}

Run:
    pip install pytest requests
    pytest test_support.py -v
"""

import pytest
import requests
from header_validation import (
    assert_missing_roll_number_returns_401,
    assert_invalid_roll_number_returns_400,
    assert_missing_user_id_returns_400,
    assert_nonexistent_user_id_returns_400,
)

BASE_URL = "http://localhost:8080/api/v1"
ROLL     = "2024111004"
USER_ID  = "1"

VALID_TICKET = {
    "subject": "Issue with my order delivery",
    "message": "My order has not arrived yet and it has been 7 days.",
}


@pytest.fixture(scope="session")
def valid_headers():
    return {"X-Roll-Number": ROLL, "X-User-ID": USER_ID}


@pytest.fixture
def created_ticket(valid_headers):
    """Create a ticket and return its ticket_id."""
    res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers, json=VALID_TICKET)
    assert res.status_code in (200, 201)
    data = res.json()
    ticket = data.get("ticket") or data
    return ticket["ticket_id"]


# ═════════════════════════════════════════════════════════════════
# 1. POST /api/v1/support/ticket
# ═════════════════════════════════════════════════════════════════

class TestCreateTicket:

    def test_valid_ticket_returns_200(self, valid_headers):
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json=VALID_TICKET)
        assert res.status_code in (200, 201)

    def test_new_ticket_status_is_open(self, valid_headers):
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json=VALID_TICKET)
        data = res.json()
        ticket = data.get("ticket") or data
        assert ticket.get("status") == "OPEN", (
            f"New ticket should start as OPEN, got {ticket.get('status')}"
        )

    def test_message_saved_exactly(self, valid_headers):
        """The full message must be stored exactly as written."""
        long_message = "This is my exact message with special chars: @#$ 1234 end."
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json={"subject": "Test subject here", "message": long_message})
        data = res.json()
        ticket = data.get("ticket") or data
        assert ticket.get("message") == long_message, (
            f"Message not stored correctly. Got: {ticket.get('message')}"
        )

    def test_subject_too_short_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json={"subject": "Hi", "message": "Some message content"})
        assert res.status_code == 400

    def test_subject_too_long_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json={"subject": "A" * 101, "message": "Some message content"})
        assert res.status_code == 400

    def test_subject_boundary_5_chars_returns_200(self, valid_headers):
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json={"subject": "Hello", "message": "Some message"})
        assert res.status_code in (200, 201)

    def test_subject_boundary_100_chars_returns_200(self, valid_headers):
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json={"subject": "A" * 100, "message": "Some message"})
        assert res.status_code in (200, 201)

    def test_message_empty_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json={"subject": "Valid subject", "message": ""})
        assert res.status_code == 400

    def test_message_over_500_chars_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json={"subject": "Valid subject", "message": "A" * 501})
        assert res.status_code == 400

    def test_message_exactly_500_chars_returns_200(self, valid_headers):
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json={"subject": "Valid subject", "message": "A" * 500})
        assert res.status_code in (200, 201)

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/support/ticket", USER_ID)

    def test_invalid_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/support/ticket", USER_ID, "abc")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/support/ticket", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/support/ticket", ROLL, "99999")


# ═════════════════════════════════════════════════════════════════
# 2. GET /api/v1/support/tickets
# ═════════════════════════════════════════════════════════════════

class TestGetTickets:

    def test_valid_request_returns_200(self, valid_headers):
        res = requests.get(f"{BASE_URL}/support/tickets", headers=valid_headers)
        assert res.status_code == 200

    def test_response_is_list(self, valid_headers):
        res = requests.get(f"{BASE_URL}/support/tickets", headers=valid_headers)
        assert isinstance(res.json(), list)

    def test_ticket_fields_present(self, valid_headers, created_ticket):
        res = requests.get(f"{BASE_URL}/support/tickets", headers=valid_headers)
        tickets = res.json()
        assert len(tickets) > 0
        ticket = tickets[0]
        for field in ("ticket_id", "subject", "message", "status"):
            assert field in ticket, f"Ticket missing field '{field}'"

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/support/tickets", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/support/tickets", ROLL)


# ═════════════════════════════════════════════════════════════════
# 3. PUT /api/v1/support/tickets/{ticket_id}
# ═════════════════════════════════════════════════════════════════

class TestUpdateTicketStatus:

    def test_open_to_in_progress_returns_200(self, valid_headers, created_ticket):
        res = requests.put(f"{BASE_URL}/support/tickets/{created_ticket}",
                           headers=valid_headers,
                           json={"status": "IN_PROGRESS"})
        assert res.status_code == 200

    def test_in_progress_to_closed_returns_200(self, valid_headers):
        """Create a ticket, advance it to IN_PROGRESS, then CLOSED."""
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json=VALID_TICKET)
        ticket_id = (res.json().get("ticket") or res.json())["ticket_id"]
        requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=valid_headers,
                     json={"status": "IN_PROGRESS"})
        res2 = requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=valid_headers,
                            json={"status": "CLOSED"})
        assert res2.status_code == 200

    def test_open_to_closed_directly_returns_400(self, valid_headers):
        """Skipping IN_PROGRESS — going directly from OPEN to CLOSED — must be rejected."""
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json=VALID_TICKET)
        ticket_id = (res.json().get("ticket") or res.json())["ticket_id"]
        res2 = requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=valid_headers,
                            json={"status": "CLOSED"})
        assert res2.status_code == 400

    def test_closed_to_open_returns_400(self, valid_headers):
        """Reversing a closed ticket must be rejected."""
        res = requests.post(f"{BASE_URL}/support/ticket", headers=valid_headers,
                            json=VALID_TICKET)
        ticket_id = (res.json().get("ticket") or res.json())["ticket_id"]
        requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=valid_headers,
                     json={"status": "IN_PROGRESS"})
        requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=valid_headers,
                     json={"status": "CLOSED"})
        res2 = requests.put(f"{BASE_URL}/support/tickets/{ticket_id}", headers=valid_headers,
                            json={"status": "OPEN"})
        assert res2.status_code == 400

    def test_nonexistent_ticket_returns_404(self, valid_headers):
        res = requests.put(f"{BASE_URL}/support/tickets/999999", headers=valid_headers,
                           json={"status": "IN_PROGRESS"})
        assert res.status_code == 404

    def test_invalid_status_value_returns_400(self, valid_headers, created_ticket):
        res = requests.put(f"{BASE_URL}/support/tickets/{created_ticket}",
                           headers=valid_headers,
                           json={"status": "PENDING"})
        assert res.status_code == 400

    def test_missing_roll_number_returns_401(self, created_ticket):
        assert_missing_roll_number_returns_401(
            f"{BASE_URL}/support/tickets/{created_ticket}", USER_ID)

    def test_missing_user_id_returns_400(self, created_ticket):
        assert_missing_user_id_returns_400(
            f"{BASE_URL}/support/tickets/{created_ticket}", ROLL)
