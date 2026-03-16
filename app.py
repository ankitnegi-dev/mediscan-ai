import boto3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

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

class MediScanHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[MediScan] {format % args}")

    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            self.serve_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"), "text/html")
        else:
            self.send_error(404)

    def serve_file(self, path, content_type):
        try:
            with open(path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/analyze":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                content_type = self.headers.get("Content-Type", "")
                body = self.rfile.read(content_length)
                boundary = None
                for part in content_type.split(";"):
                    part = part.strip()
                    if part.startswith("boundary="):
                        boundary = part[9:].strip()
                        break
                if not boundary:
                    self.send_json_error("No file boundary found"); return
                file_bytes, file_mime = self.parse_multipart(body, boundary)
                if not file_bytes:
                    self.send_json_error("No file data received"); return
                result = analyze_report(file_bytes, file_mime)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                print(f"Error: {e}")
                self.send_json_error(str(e))

        elif self.path == "/translate":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                payload = json.loads(body)
                language = payload.get("language", "Hindi")
                data = payload.get("data", {})
                result = translate_report(data, language)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                print(f"Translation error: {e}")
                self.send_json_error(str(e))
        else:
            self.send_error(404)

    def parse_multipart(self, body: bytes, boundary: str):
        boundary_bytes = f"--{boundary}".encode()
        parts = body.split(boundary_bytes)
        for part in parts:
            if b"Content-Disposition" not in part: continue
            if b'name="file"' not in part and b"filename=" not in part: continue
            header_end = part.find(b"\r\n\r\n")
            if header_end == -1: continue
            headers_raw = part[:header_end].decode("utf-8", errors="ignore")
            file_data = part[header_end + 4:]
            if file_data.endswith(b"\r\n"): file_data = file_data[:-2]
            mime_type = "application/pdf"
            for line in headers_raw.split("\r\n"):
                if "Content-Type:" in line:
                    mime_type = line.split(":", 1)[1].strip()
            return file_data, mime_type
        return None, None

    def send_json_error(self, message: str):
        error = {"error": message}
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(error).encode())

if __name__ == "__main__":
    port = 8080
    server = HTTPServer(("0.0.0.0", port), MediScanHandler)
    print(f"MediScan AI running at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
