# MediScan AI 🩺
### Smart Medical Report Analyzer — Amazon Nova AI Hackathon 2026

> Upload any medical report → AI reads, explains, and translates it in 22 Indian languages — powered by Amazon Nova Pro

![Amazon Nova](https://img.shields.io/badge/Amazon_Nova-Pro-FF9900?style=flat-square&logo=amazonaws)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python)
![Amazon Bedrock](https://img.shields.io/badge/Amazon_Bedrock-Converse_API-FF9900?style=flat-square&logo=amazonaws)
![Languages](https://img.shields.io/badge/Languages-22_Indian-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

---

## 🎥 Demo

[![MediScan AI Demo](https://img.youtube.com/vi/zXqR175jmhM/0.jpg)](https://www.youtube.com/watch?v=zXqR175jmhM)

> Upload a blood test, X-ray report, or prescription → Nova reads it → Results appear in your language

**[▶ Watch Full Demo on YouTube](https://www.youtube.com/watch?v=zXqR175jmhM)**
```

---

## ✨ Features

### 🤖 Intelligent Medical Analysis
| Feature | Description |
|---------|-------------|
| 📄 Multimodal Input | Accepts PDF, JPG, PNG, WebP medical documents |
| 🔍 Auto Extraction | Extracts ALL findings from any report automatically |
| 🎨 Color Coding | 🟢 Normal · 🟠 Warning · 🔴 Critical |
| 📏 Reference Ranges | Shows "Your value: 8.8 \| Normal: 8.4–10.4 mg/dl" |
| 💡 Plain Language | Explains results like a 12-year-old can understand |
| 📋 Next Steps | Suggests specialist referrals and recommended actions |

### 🌐 22 Official Indian Languages
- Single elegant dropdown with **live search** — find your language in seconds
- **Entire UI translates** — buttons, labels, loading steps, status badges, disclaimers
- Medical content translated via a dedicated Amazon Nova API call
- Translations **cached** — switch between languages instantly after first load
- Spinner indicator while Nova translates in real time

### 📊 Report History & Export
- Last 5 reports **saved automatically** in browser
- Switch between old and new reports with one click — compare over time
- **One-click PDF download** — clean print layout, UI controls hidden automatically

---

## 🌍 Languages Supported

Hindi · Bengali · Telugu · Marathi · Tamil · Gujarati · Kannada · Malayalam · Punjabi · Odia · Assamese · Urdu · Maithili · Santali · Kashmiri · Nepali · Sindhi · Konkani · Dogri · Manipuri · Bodo · Sanskrit

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Model** | Amazon Nova Pro (`amazon.nova-pro-v1:0`) |
| **Cloud** | Amazon Bedrock (Converse API) |
| **Backend** | Python 3 (stdlib only + boto3) |
| **Frontend** | Pure HTML / CSS / JS (zero frameworks) |
| **File Support** | PDF, JPEG, PNG, WebP |
| **Fonts** | DM Serif Display, DM Sans (Google Fonts) |

> 💡 **Minimal dependencies** — only `boto3` required. No React, no Node, no build step.

---

## 📁 Project Structure

```
mediscan-ai/
├── app.py           # Python backend + Amazon Nova integration + /translate endpoint
├── index.html       # Complete frontend — UI + 22-language support + history
├── requirements.txt # Python dependencies (boto3 only)
└── README.md        # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- AWS Account with Amazon Bedrock access
- Nova Pro model enabled in `us-east-1`

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/mediscan-ai.git
cd mediscan-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output: press Enter

### Enable Nova Pro in Amazon Bedrock
1. Go to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click **Model access** in the left sidebar
3. Find **Amazon Nova Pro** and enable it

### Run the App

```bash
python3 app.py
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

---

## 🌐 How It Works

```
User uploads medical report (PDF or image)
            ↓
POST /analyze → Python backend
            ↓
Amazon Nova Pro (multimodal) reads the document
            ↓
Agentic reasoning: extract → classify → explain → recommend
            ↓
Structured JSON response returned to frontend
            ↓
Results rendered: color-coded findings + reference ranges + next steps
            ↓
User clicks a language button (e.g. हिंदी)
            ↓
POST /translate → Amazon Nova Pro translates on demand
            ↓
Full UI + medical content switches to chosen language
```

---

## 🔧 Key Implementation Details

### Agentic Analysis Prompt
Nova acts as an autonomous agent — no step-by-step prompting needed:
```python
SYSTEM_PROMPT = """You are MediScan AI. Given a medical report, autonomously:
1. Extract ALL findings with reference ranges
2. Classify each as normal | warning | critical
3. Generate plain-language explanations
4. Suggest next steps
Return structured JSON only."""
```

### Multimodal Input Handling
Supports both PDF documents and images:
```python
if file_type in ["image/jpeg", "image/png", "image/webp"]:
    content_block = {"image": {"format": fmt, "source": {"bytes": file_bytes}}}
else:
    content_block = {"document": {"format": "pdf", "name": "report", "source": {"bytes": file_bytes}}}
```

### On-Demand Translation
Separate Nova call — only triggered when user picks a language:
```python
def translate_report(data: dict, language: str) -> dict:
    # Translates summary, reassurance, and all finding explanations
    # Returns JSON with translated fields only
    # Frontend caches result — no repeat API calls
```

---

## 🧪 Real-World Test

Tested on actual blood reports from **Tagore Medical College & Hospital, Chennai**:

| Finding | Value | Status | Reference |
|---------|-------|--------|-----------|
| Calcium | 8.8 mg/dl | 🟢 Normal | 8.4–10.4 mg/dl |
| Vitamin D | <8.1 NG/ML | 🔴 Critical | 30–100 NG/ML |
| WBC Count | 5780 cells/cu.mm | 🟢 Normal | 4,000–10,000 |
| Haemoglobin | 13.4 gms/dl | 🟢 Normal | M: 13–17 |
| Platelet Count | 1.58 Lakhs/cu.mm | 🟢 Normal | 1.5–4.5 |

✅ Correctly identified critical Vitamin D deficiency
✅ Matched lab reference values exactly
✅ Translated accurately into Hindi, Tamil, Bengali and more

---

## 💡 Inspiration

1.4 billion Indians receive medical reports they cannot understand. Most wait days for a doctor appointment just to be told what their blood test means. Rural patients, elderly citizens, and non-English speakers are most affected.

MediScan AI bridges this gap — giving every Indian **immediate, clear, compassionate** understanding of their own health data in their own language.

---

## 🔮 What's Next

- 🎙️ Voice readout using **Amazon Nova Sonic**
- 📈 Trend graphs comparing multiple reports over time
- 🏥 Hospital appointment booking integration
- 📱 WhatsApp bot for rural India
- 🔬 X-ray and MRI image analysis

---

## 🏆 Hackathon Info

- **Event:** Amazon Nova AI Hackathon 2026
- **Tracks:** Multimodal Understanding + Agentic AI
- **Deadline:** March 17, 2026 @ 5:30am IST
- **Prize Pool:** $40,000 cash + $55,000 AWS credits
- **Hashtag:** #AmazonNova

---

## 📝 Resume Line

> *Built an AI-powered medical report analyzer using Amazon Nova Pro's multimodal and agentic capabilities. Supports all 22 official Indian languages with on-demand translation, reference range display, report history, and PDF export — making healthcare accessible to 1.4 billion Indians.*

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT © 2026

---

<p align="center">Built with ❤️ for India · Powered by Amazon Nova</p>
