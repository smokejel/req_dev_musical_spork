# Quick Model Reference Guide

**For developers who need model names fast!**

---

## TL;DR - Use These Models

### For This Project (Phase 0)
```python
# Skills validation test
model = "claude-sonnet-4-5-20250929"
```

### For This Project (Phase 1-4 MVP)
```python
# Extract node
extract_model = "gpt-4o-mini"

# Analyze node
analyze_model = "claude-sonnet-4-5-20250929"

# Decompose node
decompose_model = "gpt-4o"

# Validate node
validate_model = "claude-sonnet-4-5-20250929"
```

---

## Model Names by Provider

### Anthropic Claude (Recommended for Quality)
```python
# Latest and greatest
"claude-sonnet-4-5-20250929"  # Best for this project
"claude-haiku-4-5-20251001"   # Fast & cheap alternative
"claude-opus-4-1-20250805"    # Most powerful (expensive)
```

### OpenAI (Recommended for Speed & Cost)
```python
# GPT-4o series (recommended)
"gpt-4o"           # Balanced performance
"gpt-4o-mini"      # Fast, cheap, great for extraction

# GPT-4.1 series (newer)
"gpt-4.1"          # Smartest non-reasoning
"gpt-4.1-mini"     # Faster version
```

### Google Gemini (Recommended for Large Context)
```python
# Gemini 2.5 series
"gemini-2.5-flash"      # Best price-performance
"gemini-2.5-pro"        # Most capable
"gemini-2.5-flash-lite" # Fastest & cheapest
```

---

## Common Mistakes to Avoid

### ❌ DON'T Use These (They Don't Exist!)
```python
"claude-3-5-sonnet-20241022"  # Deprecated/retired
"claude-3-5-sonnet-20240620"  # Deprecated/retired
"claude-3-5-sonnet-latest"    # Alias, unstable for production
"gpt-4-latest"                # Alias, use specific version
```

### ✅ DO Use These Instead
```python
"claude-sonnet-4-5-20250929"  # Current Claude Sonnet
"gpt-4o"                      # Current GPT-4o
"gemini-2.5-flash"            # Current Gemini Flash
```

---

## Quick Comparison

| Need | Model | Why |
|------|-------|-----|
| **Quality reasoning** | `claude-sonnet-4-5-20250929` | Best architectural analysis |
| **Fast & cheap** | `gpt-4o-mini` | 90% cheaper than GPT-4o |
| **Huge context** | `gemini-2.5-pro` | 1M token window |
| **JSON extraction** | `gpt-4o-mini` | Excellent structured output |
| **Code generation** | `claude-sonnet-4-5-20250929` | Top coding performance |
| **Validation** | `claude-sonnet-4-5-20250929` | Critical evaluation |

---

## Pricing Cheat Sheet (Per 1M Tokens)

| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| GPT-4o mini | ~$0.15 | ~$0.60 | Budget extraction |
| GPT-4o | ~$2.50 | ~$10 | Balanced tasks |
| Claude Haiku 4.5 | $1 | $5 | Fast, affordable |
| Claude Sonnet 4.5 | $3 | $15 | Quality work |
| Claude Opus 4.1 | $15 | $75 | Premium quality |
| Gemini 2.5 Flash | ~$0.075 | ~$0.30 | Very cheap |

---

## Code Templates

### Anthropic Claude
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0.0,
    max_tokens=4096
)
```

### OpenAI
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.0,
    max_tokens=4096
)
```

### Google Gemini
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
    max_output_tokens=4096
)
```

---

## Temperature Settings

```python
# For deterministic outputs (requirements extraction)
temperature = 0.0

# For creative tasks (none in this project)
temperature = 0.7

# For architectural analysis (slight creativity)
temperature = 0.1
```

---

## When Models Fail

### Error: "Model not found" (404)
**Fix:** Check model name spelling, use exact version from this guide

### Error: "Authentication failed" (401)
**Fix:** Check `.env` file has correct API key

### Error: "Rate limit exceeded" (429)
**Fix:** Wait 60 seconds, implement exponential backoff

### Error: "Invalid JSON response"
**Fix:** Switch to fallback model (see `MODEL_DEFINITIONS.md`)

---

## Need More Detail?

See `config/MODEL_DEFINITIONS.md` for:
- Complete model specifications
- Deprecation timelines
- Detailed pricing
- Capabilities comparison
- Error handling strategies

---

**Last Updated:** 2025-10-30
**Quick Check:** If this guide is >6 months old, check official docs for updates!
