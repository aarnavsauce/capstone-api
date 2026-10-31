import hmac
import hashlib
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

# Helper fixtures for setup
@pytest.fixture
def test_users():
    # Create Alice (Victim)
    res_a = client.post("/v1/customers", json={"name": "Alice Test", "email": "alice.test@example.com"})
    alice_id = res_a.json()["id"]
    alice_token = client.post("/v1/auth/login", json={"customerId": alice_id}).json()["access_token"]
    
    # Create Bob (Attacker)
    res_b = client.post("/v1/customers", json={"name": "Bob Test", "email": "bob.test@example.com"})
    bob_id = res_b.json()["id"]
    bob_token = client.post("/v1/auth/login", json={"customerId": bob_id}).json()["access_token"]
    
    return {
        "alice": {"id": alice_id, "token": alice_token},
        "bob": {"id": bob_id, "token": bob_token}
    }

# --- HAPPY PATH TESTS ---

def test_01_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_02_create_customer():
    response = client.post("/v1/customers", json={"name": "Charlie", "email": "charlie@example.com"})
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == "Charlie"

def test_03_login_success(test_users):
    alice_id = test_users["alice"]["id"]
    response = client.post("/v1/auth/login", json={"customerId": alice_id})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_04_create_order_authorized(test_users):
    alice = test_users["alice"]
    headers = {"Authorization": f"Bearer {alice['token']}"}
    payload = {"customerId": alice["id"], "items": [{"productId": "prod_1", "quantity": 2}]}
    
    response = client.post("/v1/orders", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["customerId"] == alice["id"]

def test_05_list_own_orders(test_users):
    alice = test_users["alice"]
    headers = {"Authorization": f"Bearer {alice['token']}"}
    response = client.get("/v1/orders", headers=headers)
    assert response.status_code == 200
    assert "items" in response.json()

# --- UNHAPPY PATH & SECURITY TESTS ---

def test_06_create_customer_invalid_email():
    response = client.post("/v1/customers", json={"name": "Invalid", "email": "not-an-email"})
    assert response.status_code == 422  # Unprocessable Entity (Validation Error)

def test_07_login_nonexistent_customer():
    response = client.post("/v1/auth/login", json={"customerId": "cust_does_not_exist"})
    assert response.status_code == 404

def test_08_order_missing_auth():
    response = client.post("/v1/orders", json={"customerId": "cust_123", "items": []})
    assert response.status_code == 403 or response.status_code == 401

def test_09_order_invalid_jwt_token():
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    response = client.get("/v1/orders", headers=headers)
    assert response.status_code == 401

def test_10_bola_attack_order_read(test_users):
    alice = test_users["alice"]
    bob = test_users["bob"]
    
    # Alice creates order
    res_order = client.post(
        "/v1/orders", 
        json={"customerId": alice["id"], "items": [{"productId": "prod_secret", "quantity": 1}]},
        headers={"Authorization": f"Bearer {alice['token']}"}
    )
    order_id = res_order.json()["id"]
    
    # Bob attempts to read Alice's order
    attack_res = client.get(f"/v1/orders/{order_id}", headers={"Authorization": f"Bearer {bob['token']}"})
    assert attack_res.status_code == 403
    assert attack_res.json()["detail"] == "Access denied: You do not own this order."

def test_11_order_spoofing_attack(test_users):
    alice = test_users["alice"]
    bob = test_users["bob"]
    
    # Bob attempts to create order for Alice
    attack_res = client.post(
        "/v1/orders",
        json={"customerId": alice["id"], "items": [{"productId": "prod_1", "quantity": 10}]},
        headers={"Authorization": f"Bearer {bob['token']}"}
    )
    assert attack_res.status_code == 403
    assert attack_res.json()["detail"] == "Forbidden: You can only place orders for your own account."

def test_12_nonexistent_order_404(test_users):
    alice = test_users["alice"]
    response = client.get("/v1/orders/ord_missing999", headers={"Authorization": f"Bearer {alice['token']}"})
    assert response.status_code == 404

# --- WEBHOOK & INTEGRATION TESTS ---

def test_13_webhook_missing_signature():
    response = client.post("/v1/webhooks/github", json={"action": "opened"})
    assert response.status_code == 401

def test_14_webhook_invalid_signature():
    headers = {
        "X-GitHub-Event": "push",
        "X-GitHub-Delivery": "del_12345",
        "X-Hub-Signature-256": "sha256=invalid_signature_hash"
    }
    response = client.post("/v1/webhooks/github", json={"ref": "refs/heads/main"}, headers=headers)
    assert response.status_code == 401

def test_15_webhook_valid_signature():
    payload = b'{"ref": "refs/heads/main"}'
    signature = "sha256=" + hmac.new(settings.WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    
    headers = {
        "X-GitHub-Event": "push",
        "X-GitHub-Delivery": "del_valid_001",
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json"
    }
    response = client.post("/v1/webhooks/github", content=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_16_webhook_duplicate_detection():
    payload = b'{"ref": "refs/heads/main"}'
    signature = "sha256=" + hmac.new(settings.WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    
    headers = {
        "X-GitHub-Event": "push",
        "X-GitHub-Delivery": "del_duplicate_002",
        "X-Hub-Signature-256": signature,
        "Content-Type": "application/json"
    }
    # First delivery
    client.post("/v1/webhooks/github", content=payload, headers=headers)
    
    # Second delivery (duplicate event ID)
    res_duplicate = client.post("/v1/webhooks/github", content=payload, headers=headers)
    assert res_duplicate.status_code == 200
    assert res_duplicate.json()["message"] == "Event already processed"

def test_17_request_id_middleware_logging():
    response = client.get("/health")
    assert "X-Request-ID" in response.headers

def test_18_openapi_docs_accessible():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == settings.APP_NAME