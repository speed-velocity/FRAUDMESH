from pathlib import Path

from app.db.database import load_dataset, network_path


def test_account_to_holder_path_includes_ownership(tmp_path):
    database = f"sqlite:///{tmp_path / 'fraudmesh.db'}"
    dataset = Path(__file__).resolve().parents[2] / "data" / "demo"
    load_dataset(str(dataset), database)
    result = network_path(database, "ACC-M1", "ENT-01")
    assert result["found"] is True
    assert result["nodes"] == ["ACC-M1", "ENT-01"]
    assert result["edges"][0]["kind"] == "account_holder"
