"""Print the current synthetic evaluation summary as JSON."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import json
from app.core.config import get_settings
from app.db.database import evaluation_summary

print(json.dumps(evaluation_summary(get_settings().database_url), indent=2, sort_keys=True))
