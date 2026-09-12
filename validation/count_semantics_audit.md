# Count semantics audit

Status: provenance probe; no artifact or estimator correction applied.
Source revision: `8cb9639eb162ff3732df82d4e190e7f902bde19d`.

| Boundary | Evidence | Established meaning | Remaining uncertainty |
| --- | --- | --- | --- |
| Paper section 3.1 | Xu et al. (2026), LaRT v4, positive integer matrix T | Model input represents positive CoT length | Does not specify a zero-count offset or combined CSV encoding |
| Paper section 7 | Each model's tokenizer counts CoT length | Length is a token observable, not wall-clock time | Does not establish the historical combined-file transformation |
| `data/README.md:16–18` | Token-count CSVs; applications add one before logarithms | Describes a count-to-positive-input conversion | Blanket wording does not explicitly distinguish the combined artifact |
| `data_generation/generate_responses.py:95` | `len(tokenizer.encode(reasoning, add_special_tokens=False))` | The sample generator's `cot_tokens` is an unshifted token count | This sample is not proof of the historical data-generation run |
| `data_generation/build_matrices.py:36–42` | Pivot `cot_tokens`, cast to integer, serialize | Sample builder adds no pseudocount | Historical combined export uses a different notebook path |
| Notebook cells 86–88 | Combine matrices, increment array, then serialize frame | Operation order is verified | Shared-storage mutation is plausible; environment and execution history are unverified |
| `src/lart/api.py:48–63` | Reject nonfinite/nonpositive T; pass unchanged | Public estimator needs positive input, not necessarily raw counts | Positive raw and shifted values cannot be distinguished numerically |
| `src/lart/estimation.py:413–517` | Log T, consume log T | No unit pseudocount in these estimator paths | This does not select a CSV storage contract |
| Two combined applications | Loader adds one to stored values | Current inference input is individual counts plus two | Intent and published-result attribution remain unknown |

Primary paper: Xu, Z., Liu, J., Wang, Y., & Gu, Y. (2026).
*Latency-response theory model: Evaluating large language models via response
accuracy and chain-of-thought length* (Version 4) [Preprint]. arXiv.
https://arxiv.org/abs/2512.07019v4

The test at `87b564fae09fdf51e89742c339d9f652361d37ca` is a probe of
raw-count preservation, not a conclusive product-defect RED. It fails for
combined lengths and passes for correctness (one unittest, 0.027s). No
dependency was installed; pandas was unavailable in the inspected interpreter.
Preserve the historical artifact until its encoding is explicitly resolved.
Neither blindly subtracting one nor changing the estimator follows from this
probe. A repair must declare the representation and validate exactly one
count-to-positive-input conversion in both consumers.
