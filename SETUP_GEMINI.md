# 🚀 Setup with Gemini + OpenAI

This guide shows how to configure Aurea Orchestrator with **Google Gemini** and **OpenAI GPT**.

## 📋 Prerequisites

1. **Google Gemini API Key**
   - Go to: https://makersuite.google.com/app/apikey
   - Create/Get your API key
   - Free tier: 60 requests/minute, very generous!

2. **OpenAI API Key** 
   - Go to: https://platform.openai.com/api-keys
   - Create API key
   - Make sure you have credits in your account

## 🔧 Configuration

### 1. Edit `.env` file

```bash
# Add your API keys
GOOGLE_API_KEY=AIzaSy...your_gemini_key_here
OPENAI_API_KEY=sk-proj-...your_openai_key_here

# Model selection
GEMINI_MODEL=gemini-1.5-pro        # or gemini-1.5-flash (faster/cheaper)
OPENAI_MODEL=gpt-4                  # or gpt-4-turbo, gpt-3.5-turbo
DEFAULT_MODEL_PROVIDER=gemini       # Use Gemini by default
```

### 2. Install Google AI Python SDK

```bash
pip install google-generativeai
```

### 3. Update requirements.txt

Add this line:
```
google-generativeai>=0.3.0
```

## 🎯 Model Strategy

**Recommended configuration:**

- **Simple tasks** (Context, Review agents) → **Gemini 1.5 Flash** 
  - Fast, cheap, excellent for analysis
  
- **Complex tasks** (Architect, Code agents) → **Gemini 1.5 Pro** or **GPT-4**
  - More powerful reasoning
  
- **Testing** (Test agent) → **Gemini 1.5 Flash**
  - Good at generating test cases

## 💰 Cost Comparison

| Model | Cost (per 1M tokens) | Best For |
|-------|---------------------|----------|
| Gemini 1.5 Flash | $0.075 input / $0.30 output | Fast tasks, high volume |
| Gemini 1.5 Pro | $3.50 input / $10.50 output | Complex reasoning |
| GPT-4 Turbo | $10 input / $30 output | Maximum capability |
| GPT-3.5 Turbo | $0.50 input / $1.50 output | Legacy fallback |

**💡 Tip:** Start with Gemini 1.5 Flash for everything. It's 50x cheaper than GPT-4 and very capable!

## 🔄 Model Router Logic

The system will automatically route based on task complexity:

```python
if complexity < 0.5:
    use_model = "gemini-1.5-flash"  # Fast & cheap
else:
    use_model = "gemini-1.5-pro"     # or "gpt-4" for max quality
```

You can adjust `COMPLEXITY_THRESHOLD` in `.env`.

## ✅ Quick Test

```bash
# 1. Setup
./setup_quick.sh

# 2. Add your API keys to .env

# 3. Test Gemini connection
python -c "
import google.generativeai as genai
genai.configure(api_key='YOUR_KEY')
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Say hello!')
print(response.text)
"

# 4. Start the system
docker-compose up
```

## 🌐 Using Microsoft 365?

If you have **Azure OpenAI** through your M365 Enterprise account:

1. Get your Azure endpoint and key from Azure Portal
2. Update `.env`:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-azure-key
AZURE_OPENAI_DEPLOYMENT=gpt-4  # your deployment name
USE_AZURE_OPENAI=true
```

**Benefits:**
- ✅ Enterprise-grade security
- ✅ Data residency compliance
- ✅ No rate limits (based on your subscription)
- ✅ Already paid through your M365 license

## 🎓 Recommended Setup for You

```env
# Primary: Gemini (cheap, fast, excellent quality)
GOOGLE_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-1.5-flash
DEFAULT_MODEL_PROVIDER=gemini

# Fallback: OpenAI (if Gemini fails or for specific tasks)
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4-turbo

# Optional: Azure OpenAI (if you have enterprise access)
AZURE_OPENAI_ENDPOINT=https://your-org.openai.azure.com/
AZURE_OPENAI_KEY=your_azure_key
```

## 📊 Expected Performance

- **Latency**: Gemini Flash ~1-2s, GPT-4 ~3-5s
- **Quality**: Both excellent for coding tasks
- **Cost**: Gemini 50-100x cheaper
- **Rate Limits**: Gemini 60 req/min (free), OpenAI 10k req/min (paid)

---

**Next Steps:**
1. Get your Gemini API key
2. Update `.env` with your keys
3. Run `./setup_quick.sh`
4. Test with a simple task!
