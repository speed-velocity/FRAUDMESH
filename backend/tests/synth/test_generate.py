import hashlib
import shutil
from pathlib import Path

from app.synth.generate import generate


def test_canonical_generation_is_deterministic():
    root = Path.cwd() / "tests" / "_generator_tmp"; shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
    try:
        first = root / "first"; second = root / "second"
        generate(out_dir=first, ground_truth_dir=root / "truth1")
        generate(out_dir=second, ground_truth_dir=root / "truth2")
        names = sorted(p.name for p in first.glob("*.json"))
        assert names == sorted(p.name for p in second.glob("*.json"))
        for name in names:
            assert hashlib.sha256((first / name).read_bytes()).digest() == hashlib.sha256((second / name).read_bytes()).digest()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_canonical_counts():
    root = Path.cwd() / "tests" / "_generator_tmp"; shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
    try:
        generate(out_dir=root / "demo", ground_truth_dir=root / "truth")
        import json
        data = lambda name: json.loads((root / "demo" / name).read_text(encoding="utf-8"))
        assert len(data("victims.json")) == 20
        assert len(data("accounts.json")) == 43
        assert len(data("transactions.json")) == 56
        assert len(data("complaints.json")) == 13
        assert len(data("communications.json")) == 9
        assert len(data("devices.json")) == 5
        assert sum(row["amount_inr"] for row in data("transactions.json")[:20]) == 913000
        assert data("manifest.json")["synthetic"] is True
    finally:
        shutil.rmtree(root, ignore_errors=True)
