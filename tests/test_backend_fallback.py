import json
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("backend_app", ROOT / "backend_app.py")
backend_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_app)


def test_predict_uses_mock_data_when_mongo_is_unavailable(monkeypatch):
    monkeypatch.setattr(backend_app, "db", None)
    req = backend_app.PredictRequest(
        diploma_percentage=85.5,
        caste_category="GOPEN",
        preferred_branches=["Computer Science and Engineering"],
        district_filters=["Amravati"],
        top_k=5,
    )

    response = backend_app.predict(req)

    assert response.dream
    assert response.realistic
    assert response.safe
    assert any(item.branch_name == "Computer Science and Engineering" for item in response.dream)
