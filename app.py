import boto3
import json
import os
from flask import Flask, request, jsonify, send_from_directory

AWS_REGION = "us-east-1"
MODEL_ID = "amazon.nova-pro-v1:0"

ANALYSIS_PROMPT = """You are MediScan AI. Analyze this medical report and return ONLY valid JSON:
{
  "patient_name": "patient name from report or null",
  "report_date": "date from report or null",
  "summary": "2-3 sentence plain English summary",
  "key_findings": [
    {
      "label": "test name",
      "value": "result with units",
      "reference_range": "normal range from report",
      "status": "normal|warning|critical",
      "explanation": "plain English explanation in 1-2 sentences"
    }
  ],
  "risk_flags": ["concerning items if any"],
  "next_steps": ["recommended actions"],
  "reassurance": "kind compassionate closing message"
}
Rules: status must be exactly normal, warning, or critical. Be compassionate. Return ONLY the JSON."""

TRANSLATE_PROMPT = """Translate the following JSON medical report analysis into {language}.
Return ONLY valid JSON with these exact keys:
{{
  "summary": "translated summary",
  "reassurance": "translated reassurance",
  "findings_explanations": ["translated explanation for each finding in order"]
}}
JSON to translate:
{content}"""


def analyze_report(file_bytes: bytes, file_type: str) -> dict:
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    if file_type in ["image/jpeg", "image/png", "image/gif", "image/webp"]:
        fmt = file_type.split("/")[1]
        content_block = {"image": {"format": fmt, "source": {"bytes": file_bytes}}}
    else:
        content_block = {"document": {"format": "pdf", "name": "medical_report", "source": {"bytes": file_bytes}}}
    messages = [{"role": "user", "content": [content_block, {"text": "Analyze this medical report. Return only valid JSON."}]}]
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": ANALYSIS_PROMPT}],
        messages=messages,
        inferenceConfig={"maxTokens": 2048, "temperature": 0.2}
    )
    raw_text = response["output"]["message"]["content"][0]["text"]
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    return json.loads(raw_text[start:end])


def translate_report(data: dict, language: str) -> dict:
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    content_to_translate = {
        "summary": data.get("summary", ""),
        "reassurance": data.get("reassurance", ""),
        "findings_explanations": [f.get("explanation", "") for f in data.get("key_findings", [])]
    }
    prompt = TRANSLATE_PROMPT.format(language=language, content=json.dumps(content_to_translate))
    messages = [{"role": "user", "content": [{"text": prompt}]}]
    response = client.converse(
        modelId=MODEL_ID,
        messages=messages,
        inferenceConfig={"maxTokens": 2048, "temperature": 0.2}
    )
    raw_text = response["output"]["message"]["content"][0]["text"]
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    return json.loads(raw_text[start:end])


# ── Flask app ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR)


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_bytes = file.read()
    file_mime = file.content_type or "application/pdf"

    if not file_bytes:
        return jsonify({"error": "Empty file received"}), 400

    try:
        result = analyze_report(file_bytes, file_mime)
        return jsonify(result)
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/translate", methods=["POST"])
def translate():
    payload = request.get_json(force=True)
    if not payload:
        return jsonify({"error": "Invalid JSON body"}), 400

    language = payload.get("language", "Hindi")
    data = payload.get("data", {})

    try:
        result = translate_report(data, language)
        return jsonify(result)
    except Exception as e:
        print(f"Translation error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = 8080
    print(f"MediScan AI running at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    app.run(host="0.0.0.0", port=port, debug=True)