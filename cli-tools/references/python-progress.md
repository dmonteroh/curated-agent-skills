# Python Progress Bars

## tqdm

```python
from tqdm import tqdm, trange

# Simple progress bar
for i in tqdm(range(100), desc="Processing"):
    process_item(i)

# Custom format
with tqdm(total=100, desc="Downloading", unit="MB") as pbar:
    for chunk in download_chunks():
        pbar.update(len(chunk))

# Multiple progress bars
for epoch in trange(10, desc="Epochs"):
    for batch in trange(100, desc="Batches", leave=False):
        train_batch(batch)
```
