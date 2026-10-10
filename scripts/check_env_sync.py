"""Check that .env.example names are represented by runtime configuration."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
env_names = {
    line.split("=", 1)[0].strip()
    for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#") and "=" in line
}
config_text = (ROOT / "backend/app/core/config.py").read_text(encoding="utf-8")
runtime_names = set(re.findall(r'alias="([A-Z][A-Z0-9_]+)"', config_text)) | {"VITE_API_ORIGIN"}
missing_from_example = sorted(runtime_names - env_names)
unknown_in_example = sorted(env_names - runtime_names)
if missing_from_example or unknown_in_example:
    raise SystemExit(f"env mismatch: missing={missing_from_example}; unknown={unknown_in_example}")
print(f"environment names synchronized: {len(env_names)}")
