# Count semantics audit

Status: local consumer correction; artifact and estimator remain unchanged.
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

## Git provenance follow-up

The non-shallow checkout traces the combined length artifact to
`a73d231f6763cf8003bf739012105b6edf831ad7` (publication-repository import).
Its blob `a6d35edec04e665780f6af9cba0eeb1ef73d9aab` is identical at the
pinned current upstream revision. There is no subsequent numeric artifact
change in the inspected path history. The initial notebook already contains
concatenation, array increment and frame export in zero-based cells 99–101;
the export then targeted `Analysis/data_original/` rather than the current
repository benchmark directory. This narrows the chronology but does not
prove which environment executed it or whether shared-array mutation occurred.

The current predictive loader was introduced with its additional unit shift
in `9955276674a24163a3abae639a6ee64e7e7a4d9a`, after the artifact import.
Its commit message describes alignment with the paper, without an explicit
combined-count encoding decision. Local tags are absent and the public
[release page](https://github.com/Toby-X/Latency-Response-Theory-Model/releases)
reported no releases on 2026-09-12. No historical intention is inferred from
that absence. The finding remains an artifact-provenance gap, not authority
to numerically rewrite published data.

## Selected compatibility contract and verification

Preserve the versioned combined artifact as count-plus-one and remove only
the extra increment in its two application consumers. This explicit
compatibility decision does not establish historical author intent. Raw
individual benchmark paths and all stored data remain unchanged.
At `911fcb1`, the exact two conversion expressions failed all six scalar
checks. At `3c52a82a8ac728c696a080f9ac2cf880094858d6`, both unittest methods
passed in 0.068s: all 25,600 retained artifact cells and six conversion cases.
The scalar frame is a test double; this does not prove pandas or estimator
integration, runtime finiteness, model accuracy, or paper-result reproduction.

Run `python -I validation/test_combined_count_contract.py` from the checkout.
No dependency installation is needed for this bounded check. The inspected
CO interpreter lacked pandas; the bundled analysis interpreter lacked scipy.
Full application and estimator integration therefore remain unverified.

Follow-up at `c1321bf4f5ba72c8835e0fd10eec6244230e2621`: the installed
analysis runtime (numpy 2.3.5, pandas 2.2.3) passed two real-pandas loading
tests in 0.250s. Run `python -I validation/test_combined_pandas_loading.py`
with those dependencies available. The exact extracted predictive loader
preserves all 12,800 encoded values, their logs are finite, and its shape and
row-order rejection checks pass. This is not a full module import or an
estimator run. The two stdlib tests also passed in 0.062s at the same head.
No dependency was installed. At prior head `2b91c30`, the changed encoding
paragraph in `data/README.md` was directly inspected in GitHub's browser
preview at 1265 × 712, English, without observed clipping or overlap; the
semantic audit table and other viewport sizes were not part of that receipt.
