# Performance Testing: Tool Examples

Use this reference for non-k6 tooling examples.

## Artillery.io

```yaml
# load-test.yml
config:
  target: 'https://api.example.com'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 300
      arrivalRate: 50
      name: "Sustained load"

  processor: "./custom-functions.js"

  variables:
    userId:
      - "user1"
      - "user2"

scenarios:
  - name: "Product browsing"
    weight: 70
    flow:
      - get:
          url: "/products"
      - think: 2
      - get:
          url: "/products/{{ $randomNumber(1, 100) }}"

  - name: "Checkout"
    weight: 30
    flow:
      - post:
          url: "/cart"
          json:
            productId: "{{ $randomNumber(1, 100) }}"
      - post:
          url: "/checkout"
          json:
            userId: "{{ userId }}"
```

## Locust (Python)

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def view_products(self):
        self.client.get("/products")

    @task(1)
    def view_product(self):
        product_id = random.randint(1, 100)
        self.client.get(f"/products/{product_id}")

    @task(1)
    def create_order(self):
        self.client.post("/orders", json={
            "product_id": random.randint(1, 100),
            "quantity": random.randint(1, 5)
        })

    def on_start(self):
        # Login or setup
        self.client.post("/login", json={
            "username": "test",
            "password": "test"
        })
```

## JMeter Thread Groups

```xml
<!-- Basic HTTP Request -->
<ThreadGroup>
  <stringProp name="ThreadGroup.num_threads">100</stringProp>
  <stringProp name="ThreadGroup.ramp_time">60</stringProp>
  <stringProp name="ThreadGroup.duration">300</stringProp>
  <boolProp name="ThreadGroup.scheduler">true</boolProp>
</ThreadGroup>
```
