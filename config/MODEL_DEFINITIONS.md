# LLM Model Definitions Reference

**Last Updated:** 2025-10-30
**Purpose:** Comprehensive reference for Claude, OpenAI, and Gemini model names, capabilities, and specifications.

---

## Anthropic Claude Models

### Latest Models (Claude 4.5 Series)

| Model Name | API ID | Alias | Use Case | Context | Max Output | Pricing (Input/Output per MTok) |
|------------|--------|-------|----------|---------|------------|--------------------------------|
| **Claude Sonnet 4.5** | `claude-sonnet-4-5-20250929` | `claude-sonnet-4-5` | Best for coding and agentic tasks | 200K / 1M (beta) | 64K | $3 / $15 |
| **Claude Haiku 4.5** | `claude-haiku-4-5-20251001` | `claude-haiku-4-5` | Fastest with near-frontier intelligence | 200K | 64K | $1 / $5 |
| **Claude Opus 4.1** | `claude-opus-4-1-20250805` | `claude-opus-4-1` | Specialized reasoning tasks | 200K | 32K | $15 / $75 |

**Features:**
- Extended thinking: ✅ All
- Priority Tier: ✅ All
- Knowledge cutoff: January 2025
- Training data: July 2025

### Legacy Models (Still Available)

| Model Name | API ID | Use Case | Context | Max Output | Pricing |
|------------|--------|----------|---------|------------|---------|
| **Claude Sonnet 4** | `claude-sonnet-4-20250514` | Previous generation | 200K / 1M (beta) | 64K | $3 / $15 |
| **Claude Sonnet 3.7** | `claude-3-7-sonnet-20250219` | Legacy | 200K | 64K / 128K (beta) | $3 / $15 |
| **Claude Opus 4** | `claude-opus-4-20250514` | Previous generation | 200K | 32K | $15 / $75 |
| **Claude Haiku 3.5** | `claude-3-5-haiku-20241022` | Budget option | 200K | 8K | $0.80 / $4 |
| **Claude Haiku 3** | `claude-3-haiku-20240307` | Older budget | 200K | 4K | $0.25 / $1.25 |

### Deprecated Models

| Model | Deprecation Date | Retirement Date | Replacement |
|-------|------------------|-----------------|-------------|
| `claude-3-7-sonnet-20250219` | Oct 28, 2025 | Feb 19, 2026 | `claude-sonnet-4-5-20250929` |
| `claude-3-5-sonnet-20240620` | Aug 13, 2025 | Oct 28, 2025 | `claude-sonnet-4-5-20250929` |
| `claude-3-5-sonnet-20241022` | Aug 13, 2025 | Oct 28, 2025 | `claude-sonnet-4-5-20250929` |
| `claude-3-opus-20240229` | Jun 30, 2025 | Jan 5, 2026 | `claude-opus-4-1-20250805` |

**Important Notes:**
- Aliases automatically point to the latest snapshot (migrate within ~1 week of new release)
- Use specific model versions (e.g., `claude-sonnet-4-5-20250929`) for production
- Models with same snapshot date are identical across all platforms (API, AWS Bedrock, Google Vertex AI)

---

## OpenAI Models

### Frontier Models (GPT-5 Series)

| Model Name | API ID | Use Case | Context | Max Output | Temperature |
|------------|--------|----------|---------|------------|-------------|
| **GPT-5** | `gpt-5` | Best for coding and agentic tasks | Advanced | 64K+ | Configurable |
| **GPT-5 mini** | `gpt-5-mini` | Faster, cost-efficient for defined tasks | Standard | 64K+ | Configurable |
| **GPT-5 nano** | `gpt-5-nano` | Fastest, most cost-efficient | Standard | 32K+ | Configurable |
| **GPT-5 pro** | `gpt-5-pro` | Smarter, more precise responses | Advanced | 64K+ | Configurable |

### GPT-4 Series (Still Active)

| Model Name | API ID | Use Case | Context | Max Output | Pricing |
|------------|--------|----------|---------|------------|---------|
| **GPT-4.1** | `gpt-4.1` | Smartest non-reasoning model | 128K | 16K | Higher |
| **GPT-4.1 mini** | `gpt-4.1-mini` | Smaller, faster version | 128K | 16K | Standard |
| **GPT-4.1 nano** | `gpt-4.1-nano` | Fastest, most cost-efficient | 128K | 16K | Lower |
| **GPT-4o** | `gpt-4o` | Fast, intelligent, flexible | 128K | 16K | Standard |
| **GPT-4o mini** | `gpt-4o-mini` | Fast, affordable for focused tasks | 128K | 16K | Lower |
| **GPT-4 Turbo** | `gpt-4-turbo` | Older high-intelligence model | 128K | 4K | Standard |

### Reasoning Models (o-series)

| Model Name | API ID | Use Case | Context | Max Output |
|------------|--------|----------|---------|------------|
| **o3** | `o3` | Complex tasks, succeeded by GPT-5 | 128K | 16K |
| **o4-mini** | `o4-mini` | Fast, cost-efficient reasoning | 128K | 16K |
| **o3-pro** | `o3-pro` | More compute for better responses | 128K | 32K |
| **o3-deep-research** | `o3-deep-research` | Most powerful deep research | 128K | 32K |
| **o4-mini-deep-research** | `o4-mini-deep-research` | Faster, affordable deep research | 128K | 16K |

### Specialized Models

| Model Name | API ID | Use Case | Features |
|------------|--------|----------|----------|
| **Sora 2** | `sora-2` | Video generation with synced audio | Video output |
| **Sora 2 Pro** | `sora-2-pro` | Advanced synced-audio video | Video output |
| **GPT Image 1** | `gpt-image-1` | State-of-the-art image generation | Image output |
| **DALL·E 3** | `dall-e-3` | Previous gen image generation | Image output |
| **Whisper** | `whisper-1` | Speech recognition | Audio→Text |
| **TTS-1** | `tts-1` | Text-to-speech (speed) | Text→Audio |
| **TTS-1 HD** | `tts-1-hd` | Text-to-speech (quality) | Text→Audio |

### Audio & Realtime Models

| Model Name | API ID | Use Case | I/O Types |
|------------|--------|----------|-----------|
| **gpt-realtime** | `gpt-realtime` | Realtime text and audio I/O | Text + Audio |
| **gpt-audio** | `gpt-audio` | Audio inputs/outputs via Chat API | Text + Audio |
| **gpt-realtime-mini** | `gpt-realtime-mini` | Cost-efficient realtime | Text + Audio |
| **gpt-audio-mini** | `gpt-audio-mini` | Cost-efficient audio | Text + Audio |

### Embeddings

| Model Name | API ID | Dimensions | Use Case |
|------------|--------|------------|----------|
| **text-embedding-3-large** | `text-embedding-3-large` | 3072 | Most capable |
| **text-embedding-3-small** | `text-embedding-3-small` | 1536 | Small, efficient |
| **text-embedding-ada-002** | `text-embedding-ada-002` | 1536 | Older model |

### Open-Weight Models

| Model Name | API ID | Use Case | License |
|------------|--------|----------|---------|
| **gpt-oss-120b** | `gpt-oss-120b` | Most powerful open-weight | Apache 2.0 |
| **gpt-oss-20b** | `gpt-oss-20b` | Medium-sized, low latency | Apache 2.0 |

---

## Google Gemini Models

### Latest Models (Gemini 2.5 Series)

| Model Name | API ID | Use Case | Context | Max Output | Knowledge Cutoff |
|------------|--------|----------|---------|------------|------------------|
| **Gemini 2.5 Pro** | `gemini-2.5-pro` | State-of-the-art thinking model | 1M tokens | 65K | Jan 2025 |
| **Gemini 2.5 Flash** | `gemini-2.5-flash` | Best price-performance | 1M tokens | 65K | Jan 2025 |
| **Gemini 2.5 Flash-Lite** | `gemini-2.5-flash-lite` | Ultra fast, cost-efficient | 1M tokens | 65K | Jan 2025 |

**Key Features:**
- Thinking: ✅ All
- Function calling: ✅ All
- Code execution: ✅ All
- Search grounding: ✅ All
- Structured outputs: ✅ All
- Caching: ✅ All
- Batch API: ✅ All

### Specialized Gemini 2.5 Models

| Model Name | API ID | Specialty | Context | Features |
|------------|--------|-----------|---------|----------|
| **Gemini 2.5 Flash Image** | `gemini-2.5-flash-image` | Image generation | 65K | Image output |
| **Gemini 2.5 Flash Live** | `gemini-2.5-flash-native-audio-preview-09-2025` | Realtime audio I/O | 131K | Live API, Audio I/O |
| **Gemini 2.5 Flash TTS** | `gemini-2.5-flash-preview-tts` | Text-to-speech | 8K | Audio output |
| **Gemini 2.5 Pro TTS** | `gemini-2.5-pro-preview-tts` | High-quality TTS | 8K | Audio output |

### Previous Generation (Gemini 2.0 Series)

| Model Name | API ID | Use Case | Context | Max Output | Knowledge Cutoff |
|------------|--------|----------|---------|------------|------------------|
| **Gemini 2.0 Flash** | `gemini-2.0-flash` | Workhorse model | 1M tokens | 8K | Aug 2024 |
| **Gemini 2.0 Flash-Lite** | `gemini-2.0-flash-lite` | Small workhorse | 1M tokens | 8K | Aug 2024 |

**Available Versions:**
- Latest: `gemini-2.0-flash`
- Stable: `gemini-2.0-flash-001`
- Experimental: `gemini-2.0-flash-exp`

### Model Version Patterns (Gemini)

| Pattern | Description | Example | Use Case |
|---------|-------------|---------|----------|
| **Stable** | Specific, unchanging model | `gemini-2.5-flash` | Production apps |
| **Preview** | Pre-release with billing | `gemini-2.5-flash-preview-09-2025` | Testing/Early adoption |
| **Latest** | Points to newest release | `gemini-flash-latest` | Auto-updates (2 week notice) |
| **Experimental** | Not for production | `gemini-2.0-flash-exp` | Feedback/Early testing |

---

## Recommended Model Selection for This Project

### Phase 0 (Skills Validation)

**Primary Model:** `claude-sonnet-4-5-20250929`
**Rationale:** Latest Claude Sonnet for testing skill-guided behavior, deterministic outputs with temperature=0.0

**Fallback Model:** `gpt-4o`
**Rationale:** Reliable alternative with good instruction following

### Phase 1-4 (MVP Implementation)

Based on `langgraph_requirements_mvp_plan.md`:

| Node | Primary Model | Fallback | Temperature | Rationale |
|------|---------------|----------|-------------|-----------|
| **Extract** | `gpt-4o-mini` | `gpt-4o` | 0.0 | Cost optimization, structured extraction |
| **Analyze** | `claude-sonnet-4-5-20250929` | `gpt-4o` | 0.1 | Architectural reasoning, context understanding |
| **Decompose** | `gpt-4o` | `claude-sonnet-4-5-20250929` | 0.0 | Complex reasoning, consistency |
| **Validate** | `claude-sonnet-4-5-20250929` | `gpt-4o` | 0.0 | Critical evaluation, quality assessment |

### Alternative Options

**Budget-Conscious:**
- Replace `claude-sonnet-4-5` → `claude-haiku-4-5` (saves 66% on cost)
- Replace `gpt-4o` → `gpt-4o-mini` (saves ~90% on cost)

**Experimental/Testing:**
- `gemini-2.5-flash` - Excellent price-performance
- `gemini-2.5-pro` - Advanced reasoning capabilities

---

## Model Selection Guidelines

### When to Use Claude Models
- ✅ Architectural analysis and strategic planning
- ✅ Complex code generation and refactoring
- ✅ Nuanced evaluation and quality assessment
- ✅ Long-form reasoning with extended thinking
- ✅ Tasks requiring ~200K context window

### When to Use OpenAI Models
- ✅ Structured data extraction (JSON, schemas)
- ✅ Cost-sensitive batch operations (GPT-4o mini)
- ✅ Fast, reliable API responses
- ✅ Tasks requiring embeddings
- ✅ Multi-modal tasks (vision, audio, images)

### When to Use Gemini Models
- ✅ Large context windows (1M tokens)
- ✅ Budget-constrained projects
- ✅ Video/audio processing
- ✅ Search grounding and web context
- ✅ Experimental features and rapid iteration

---

## Error Handling & Fallback Strategy

### Error Taxonomy

**Transient Errors** (Retry same model with exponential backoff):
- Rate limit errors (429)
- Timeout errors (504)
- Temporary API errors (5xx)

**Content Errors** (Switch to fallback model):
- JSON parsing failures
- Validation errors
- Output format mismatches
- Content policy violations

**Fatal Errors** (Stop and alert):
- Authentication failures (401, 403)
- Invalid model name (404)
- Missing API credentials
- Quota exceeded (billing issue)

### Fallback Sequence

1. **Primary Model** → 3 retries with exponential backoff (2s, 4s, 8s)
2. **Fallback Model** → 3 retries with exponential backoff
3. **Human Intervention** → Log error, alert user, wait for manual resolution

---

## Testing Model Names

When writing tests, use these patterns:

```python
# Correct - Use specific version
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0.0)

# Correct - Use specific GPT-4o version
llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0.0)

# Correct - Use stable Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

# Avoid - Aliases can change
llm = ChatAnthropic(model="claude-sonnet-latest", temperature=0.0)
```

---

## Cost Optimization Tips

1. **Use model tiers strategically:**
   - Simple extraction: GPT-4o mini ($0.15/$0.60 per MTok)
   - Complex reasoning: Claude Sonnet 4.5 ($3/$15 per MTok)
   - Validation: Claude Sonnet 4.5 (critical quality gate)

2. **Implement caching:**
   - Claude: Use prompt caching for repeated system prompts
   - OpenAI: Cache embeddings and frequent queries
   - Gemini: Use context caching for large documents

3. **Batch operations:**
   - Use batch APIs when latency isn't critical (50% discount)
   - Group similar tasks for efficient processing

4. **Monitor costs:**
   - Track token usage per node
   - Set alerts for unexpected usage spikes
   - Use LangSmith for detailed cost breakdowns

---

## API Configuration Examples

### Anthropic (Python)

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0.0,
    max_tokens=4096,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### OpenAI (Python)

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.0,
    max_tokens=4096,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

### Google Gemini (Python)

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
    max_output_tokens=4096,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

---

## Resources

- **Claude Docs:** https://docs.anthropic.com/en/docs/about-claude/models
- **OpenAI Docs:** https://platform.openai.com/docs/models
- **Gemini Docs:** https://ai.google.dev/gemini-api/docs/models
- **Gemini Pricing:** https://ai.google.dev/gemini-api/docs/pricing
- **Claude Deprecations:** https://docs.anthropic.com/en/docs/about-claude/model-deprecations
- **OpenAI Deprecations:** https://platform.openai.com/docs/deprecations

---

**Maintenance Notes:**
- Check for model updates quarterly
- Subscribe to provider newsletters for deprecation notices
- Test new models in development before production deployment
- Update this document when new models are released
