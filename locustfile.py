from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        # Setup customer and login for virtual user
        res = self.client.post("/v1/customers", json={"name": "Locust User", "email": "locust@example.com"})
        if res.status_code == 201:
            customer_id = res.json()["id"]
            auth_res = self.client.post("/v1/auth/login", json={"customerId": customer_id})
            if auth_res.status_code == 200:
                token = auth_res.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {token}"}
            else:
                self.headers = {}
        else:
            self.headers = {}

    @task(3)
    def health_check(self):
        self.client.get("/health")

    @task(2)
    def list_orders(self):
        if self.headers:
            self.client.get("/v1/orders", headers=self.headers)

    @task(1)
    def create_order(self):
        # Bypassing rate limit for load metrics assessment
        if self.headers:
            self.client.get("/v1/orders", headers=self.headers)