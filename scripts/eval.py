"""Print the current synthetic evaluation summary as JSON."""
import json
from app.core.config import get_settings
from app.db.database import evaluation_summary

print(json.dumps(evaluation_summary(get_settings().database_url), indent=2, sort_keys=True))
