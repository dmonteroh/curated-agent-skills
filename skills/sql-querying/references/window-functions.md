# Window Functions (High-Signal)

Use window functions for ranking, running totals, and time-based comparisons without losing row-level detail.

## Ranking

```sql
SELECT
  customer_id,
  order_id,
  order_date,
  ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
FROM orders;
```

Top-1 per group:

```sql
SELECT *
FROM (
  SELECT
    customer_id,
    order_id,
    order_date,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) AS rn
  FROM orders
) x
WHERE rn = 1;
```

## Running Totals / Rolling Averages

```sql
SELECT
  day,
  revenue,
  SUM(revenue) OVER (ORDER BY day) AS cumulative_revenue,
  AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7d_avg
FROM daily_sales;
```

## LAG / LEAD (Time Comparisons)

```sql
SELECT
  day,
  revenue,
  revenue - LAG(revenue) OVER (ORDER BY day) AS delta
FROM daily_sales;
```

## Common Gotchas

- Always specify `ORDER BY` when you mean “sequence”.
- Be explicit with frames (`ROWS BETWEEN ...`) for rolling windows.
- Don’t mix `RANGE` vs `ROWS` without understanding how it groups ties.
