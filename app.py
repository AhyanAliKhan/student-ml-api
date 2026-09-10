"""student-ml-api — simple prediction service for MLOps workflow exercise."""

from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

APPLICATION_NAME = "student-ml-api"
MODEL_VERSION = "model-0"


def get_version() -> str:
    """Read application version from VERSION file."""
    version_file = Path(__file__).resolve().parent / "VERSION"
    return version_file.read_text(encoding="utf-8").strip()


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "application": APPLICATION_NAME,
            "version": get_version(),
        }
    )


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "value" not in payload:
        return jsonify({"error": "Missing required field: value"}), 400

    value = payload["value"]
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return jsonify({"error": "Field 'value' must be a number"}), 400

    # Simple deterministic "model": prediction = 2 * input
    prediction = value * 2
    return jsonify({"input": value, "prediction": prediction})


if __name__ == "__main__":
    # Bind to all interfaces so the service is reachable inside containers.
    app.run(host="0.0.0.0", port=5000)
