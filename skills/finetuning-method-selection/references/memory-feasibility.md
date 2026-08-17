# Memory feasibility worksheet

Planning arithmetic for deciding whether a size class, method, and batch/sequence combination fits an available memory budget before a run is committed. This is estimation, not a guarantee — size with headroom rather than to the byte.

Every example here is labelled by **size class**, never by model name. A named-model list turns over on the vendor's schedule and becomes a maintenance subscription; the arithmetic below does not.

## The four terms

Total footprint ≈ **weights + optimizer states + gradients + activations**, plus a near-zero term for adapters. Work each term from parameter count and dtype, then sum.

### 1. Weights — `params × bytes per param`

| dtype | bytes per param |
| --- | --- |
| fp32 | 4 |
| bf16 / fp16 | 2 |
| int8 | 1 |
| int4 (4-bit quantized) | 0.5 |

The formula is the same across methods; the *result* is not, because the dtype differs. Weights loaded at 2 bytes per param and the same parameter count loaded at 0.5 are a factor of four apart. Reuse the formula freely; never reuse a weight-memory number computed for one method's dtype when sizing another's.

This term dominates full fine-tuning.

### 2. Optimizer states — trainable parameters only

| Optimizer | bytes per trainable param |
| --- | --- |
| Adam-family, fp32 states | 8 (4 momentum + 4 variance) |
| Adam-family, 8-bit states | ≈2 (quantized momentum + variance) |

Full fine-tuning carries this for every parameter. Adapter methods carry it only for the adapter, which is why the term is negligible for them at any base size.

### 3. Gradients — trainable parameters only

Same dtype as the compute precision, so typically 2 bytes per trainable parameter. Frozen base weights never accumulate a gradient, so adapter methods pay this only on the adapter.

### 4. Activations

The hardest term to pin to a number: it scales with batch size, sequence and concatenation length, and architecture, not with parameter count alone. Two levers matter more than precise estimation.

- **Gradient checkpointing** trades recompute for activation memory — a recompute pass per checkpointed segment in exchange for not holding those activations. Savings figures circulate for this; they are workload-dependent and none of the sources consulted derives one, so none is reproduced here. Measure it on the actual run rather than budgeting against a quoted percentage.
- **Sequence length** is a more direct lever on this term than batch size.

### 5. Adapter overhead

A rank-`r` adapter on a linear layer with `in` inputs and `out` outputs adds `r × (in + out)` parameters — one `r × in` factor and one `out × r` factor. At ordinary ranks this is a fraction of a percent of base model size; round it to zero in the worksheet unless an unusually high rank is in play.

## Worked size-class examples

All figures below are computed from the tables above, in decimal GB. They are arithmetic, not measurements.

**8B-class, bf16, adapter method.** Weights `8e9 × 2 = 16 GB`. Optimizer state and gradients are adapter-only and round to zero. Total before activations: **≈16 GB** — the reference point for "an 8B-class model fits comfortably on a single high-memory device in bf16 with an adapter".

**8B-class, 4-bit quantized, adapter method.** Weights `8e9 × 0.5 = 4 GB`. Total before activations: **≈4 GB**. Roughly a quarter of the bf16 figure — which is why quantizing buys headroom for a larger batch or a longer sequence at the same size class, not only the ability to fit a bigger model.

**8B-class, bf16, full fine-tune.** Weights `16 GB` + gradients `8e9 × 2 = 16 GB` + optimizer `8e9 × 8 = 64 GB` = **≈96 GB** before activations, or **≈48 GB** with 8-bit optimizer states (`8e9 × 2 = 16 GB` for that term). The gap between this and the 16 GB adapter figure is the entire reason adapter methods exist at this size class.

**70B-class, 4-bit quantized, adapter method.** Weights `70e9 × 0.5 = 35 GB`. Treat **≈40 GB** as the working anchor once quantization metadata and runtime overhead are counted — the 40 is a chosen adjustment with a stated mechanism, not a measured value; the 35 is arithmetic. The same size class in bf16 puts weights alone at `70e9 × 2 = 140 GB`, before optimizer state, gradients, or activations.

## Using the worksheet

1. Fix the size class and the method.
2. Sum weights, optimizer states, and gradients from the tables, using the dtype that method actually loads at.
3. Add activations, and treat any checkpointing saving as unknown until measured on the run.
4. Compare against the nearest worked example above. An estimate far off an anchor for the same size class and method is a signal to recheck the dtype and the method assumption, not a signal to add headroom and proceed.
