```text
# 1. Create Users
$alice = Invoke-RestMethod -Uri "[http://127.0.0.1:8000/v1/customers](http://127.0.0.1:8000/v1/customers)" -Method Post -ContentType "application/json" -Body '{"name": "Alice Victim", "email": "alice@example.com"}'

$bob = Invoke-RestMethod -Uri "[http://127.0.0.1:8000/v1/customers](http://127.0.0.1:8000/v1/customers)" -Method Post -ContentType "application/json" -Body '{"name": "Bob Attacker", "email": "bob@example.com"}'

# 2. Get Access Tokens
$aliceToken = (Invoke-RestMethod -Uri "[http://127.0.0.1:8000/v1/auth/login](http://127.0.0.1:8000/v1/auth/login)" -Method Post -ContentType "application/json" -Body "{`"customerId`": `"$($alice.id)`"}").access_token

$bobToken = (Invoke-RestMethod -Uri "[http://127.0.0.1:8000/v1/auth/login](http://127.0.0.1:8000/v1/auth/login)" -Method Post -ContentType "application/json" -Body "{`"customerId`": `"$($bob.id)`"}").access_token

# 3. Create Order as Alice
$order = Invoke-RestMethod -Uri "[http://127.0.0.1:8000/v1/orders](http://127.0.0.1:8000/v1/orders)" -Method Post -Headers @{ Authorization = "Bearer $aliceToken" } -ContentType "application/json" -Body (@{ customerId = $alice.id; items = @(@{ productId = "prod_99"; quantity = 1 }) } | ConvertTo-Json -Depth 3)

# 4. BOLA Attack Test (Bob attempts to read Alice's order -> Expects 403)
try { Invoke-RestMethod -Uri "[http://127.0.0.1:8000/v1/orders/$($order.id](http://127.0.0.1:8000/v1/orders/$($order.id))" -Method Get -Headers @{ Authorization = "Bearer $bobToken" } } catch { $_.Exception.Message }

# 5. Rate Limiter Test (6 rapid requests -> Expects 429 on 6th request)
1..6 | ForEach-Object { try { $res = Invoke-RestMethod -Uri "[http://127.0.0.1:8000/v1/orders](http://127.0.0.1:8000/v1/orders)" -Method Post -Headers @{ Authorization = "Bearer $bobToken" } -ContentType "application/json" -Body (@{ customerId = $bob.id; items = @(@{ productId = "prod_99"; quantity = 1 }) } | ConvertTo-Json -Depth 3); "Req ${_}: Created$($res.id)" } catch { "Req ${_}: Blocked ($($_.Exception.Message))" } }

```
