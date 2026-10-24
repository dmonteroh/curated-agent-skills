# Capacity Planning: Forecasting and Trends

Use this reference for growth projection methods and trend analysis queries.

## Growth Projection

### Linear Projection

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Historical data
data = pd.DataFrame({
    'month': range(1, 13),
    'requests_per_second': [100, 120, 145, 160, 180, 200, 220, 245, 270, 290, 310, 330]
})

# Train model
model = LinearRegression()
X = data[['month']].values
y = data['requests_per_second'].values
model.fit(X, y)

# Forecast next 6 months
future_months = np.array([[13], [14], [15], [16], [17], [18]])
predictions = model.predict(future_months)

print("Projected RPS in 6 months:", predictions[-1])
```

### Prometheus Queries for Trends

```promql
# Monthly growth rate
(
  rate(http_requests_total[30d])
  /
  rate(http_requests_total[30d] offset 30d)
) - 1

# Predict resource exhaustion
predict_linear(
  node_memory_MemAvailable_bytes[1h],
  3600 * 24 * 30  # 30 days ahead
)

# Storage growth
predict_linear(
  node_filesystem_avail_bytes[7d],
  3600 * 24 * 90  # 90 days ahead
)
```
