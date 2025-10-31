# Requirements Extraction Methodology

## Purpose
Extract atomic, testable requirements from system specifications.

## CRITICAL: ID Format Requirements
**You MUST use this exact ID format:**
- Format: `EXTRACT-{{TYPE}}-{{NUM}}`
- {{TYPE}} must be one of: `FUNC`, `PERF`, `CONS`, `INTF`
- {{NUM}} must be zero-padded 3 digits: `001`, `002`, `003`, etc.

**Examples of CORRECT IDs:**
- `EXTRACT-FUNC-001` (functional requirement #1)
- `EXTRACT-PERF-012` (performance requirement #12)
- `EXTRACT-CONS-003` (constraint requirement #3)
- `EXTRACT-INTF-001` (interface requirement #1)

**Examples of INCORRECT IDs (DO NOT USE):**
- ❌ `REQ-001` (missing EXTRACT prefix and type code)
- ❌ `EXTRACT-FUNCTIONAL-001` (type must be 4-letter code)
- ❌ `EXTRACT-FUNC-1` (number must be zero-padded)

## Process

### Step 1: Identify Requirements
Look for statements with modal verbs (shall, must, should, may) or imperative language.

### Step 2: Categorize
- **Functional (FUNC):** What the system does
- **Performance (PERF):** How well it does it (speed, accuracy, capacity)
- **Constraint (CONS):** Limitations or restrictions
- **Interface (INTF):** External system interactions

### Step 3: Extract with Metadata
Each requirement must include ALL four fields:
1. **id:** Use format `EXTRACT-{{TYPE}}-{{NUM}}` (see ID format requirements above)
2. **text:** Full requirement text (exact quote or minimal paraphrase for clarity)
3. **type:** One of: `functional`, `performance`, `constraint`, `interface`
4. **source_reference:** Where in document (e.g., "Section 2.1", "Paragraph 3", "Table 1")

### Step 4: Quality Check
Each requirement must be:
- ✓ Atomic (single, testable statement)
- ✓ Unambiguous (single interpretation)
- ✓ Measurable (clear acceptance criteria)

## Output Format (REQUIRED)
**You MUST return a valid JSON array with this exact structure:**

```json
[
  {{
    "id": "EXTRACT-FUNC-001",
    "text": "The system shall process user requests",
    "type": "functional",
    "source_reference": "Section 2.1"
  }},
  {{
    "id": "EXTRACT-PERF-001",
    "text": "The system shall process requests within 100ms",
    "type": "performance",
    "source_reference": "Section 3.2"
  }}
]
```

**Important JSON Rules:**
- Wrap entire output in square brackets `[ ]`
- Each requirement is a separate object in curly braces `{{ }}`
- Use commas between requirements
- Enclose all strings in double quotes
- Escape special characters (quotes, newlines) properly
- Do NOT include any text before or after the JSON array

## Complete Example

**Source Document:**
```
REQUIREMENTS
The system shall authenticate users via OAuth 2.0.
Response time must not exceed 200ms for 95th percentile requests.
```

**Correct Output:**
```json
[
  {{
    "id": "EXTRACT-FUNC-001",
    "text": "The system shall authenticate users via OAuth 2.0",
    "type": "functional",
    "source_reference": "REQUIREMENTS, Paragraph 1"
  }},
  {{
    "id": "EXTRACT-PERF-001",
    "text": "Response time must not exceed 200ms for 95th percentile requests",
    "type": "performance",
    "source_reference": "REQUIREMENTS, Paragraph 2"
  }}
]
```
