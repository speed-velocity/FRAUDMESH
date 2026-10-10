# Synthetic evaluation

FraudMesh reports evaluation separately from production performance. The event stream is split by the dataset's `held_out` flag: records marked `false` are DEV records and records marked `true` are HELD-OUT records. The held-out stream is replayed by the Event simulator and is not used to tune deterministic rules.

`python scripts/eval.py` prints JSON with held-out coverage, precision, recall, false positives, per-rule hits, and a confusion summary. Coverage is detected expected positives divided by expected positives. A predicted positive is a held-out transaction whose source or destination account is surfaced by the deterministic risk pipeline. These are synthetic signals only, not production model metrics.

The current ground truth is synthetic and includes mule fan-in, rapid forwarding, cash-out, and complaint-linked scenarios. It does not establish guilt, intent, or real-world model quality. Review the per-rule and false-negative fields before interpreting the result.
