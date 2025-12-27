# Domain-Aware Requirements Decomposition System - Implementation Plan

**Phase 7: Domain Awareness and CSX Railway Integration**

**Status:** Planning Complete - Ready for Implementation
**Location:** `docs/phases/phase7/implementation_plan.md`
**Timeline:** 10-14 days across 7 implementation phases

## Executive Summary

This plan adapts the generic requirements decomposition system for CSX Railway dispatch system domain knowledge while maintaining flexibility for other subsystems (Train Management, Traffic Control, Bridge Control, etc.). The solution introduces a **3-tier domain context architecture** that separates common domain knowledge from subsystem-specific context, enabling zero-code-change extensibility for new subsystems.

### Key Design Decisions

1. **Domain Context Architecture**: 3-tier structure (Common → Subsystem-Specific → Examples)
2. **Flexible Injection**: Domain context is optional and injected at runtime via CLI parameters
3. **Quality Enhancement**: Add 5th quality dimension "Domain Compliance" (20% weight) for CSX-specific validation
4. **Requirement Sectioning**: Post-processing approach to group requirements logically (Initiation → Processing → Completion)
5. **Backward Compatibility**: System remains fully functional in generic mode without domain context

---

## Architecture Overview

### Domain Context Layers

```
domain_contexts/
├── csx_railway/                           # Domain root
│   ├── common/                            # Layer 1: Shared across all CSX subsystems
│   │   ├── doc_conventions.md             # Requirement template, style guide
│   │   ├── glossary.md                    # Capitalized terms dictionary (~100 terms)
│   │   └── system_overview.md             # SRS high-level context
│   └── subsystems/                        # Layer 2: Subsystem-specific
│       ├── train_management/
│       │   ├── overview.md                # TM subsystem purpose, context, actors
│       │   └── examples/                  # Layer 3: Few-shot learning (optional)
│       │       └── uc_tm_040.md           # UC-TM-040 benchmark example
│       ├── traffic_control/
│       │   └── overview.md
│       └── bridge_control/
│           └── overview.md
```

### Domain Injection Points by Node

| Node | Domain Context Used | Purpose |
|------|---------------------|---------|
| **Extract** | Conventions + Glossary | Parse requirements following CSX template format |
| **Analyze** | System Overview + Subsystem Overview | Create allocation rules with CSX terminology |
| **Decompose** | Conventions + Glossary + Subsystem Context | Write requirements following CSX standards |
| **Validate** | Conventions + Glossary | Check domain compliance (5th quality dimension) |

---

## State Schema Extensions

### New Fields in `DecompositionState` (src/state.py)

```python
# ========================================================================
# Domain Context (Optional - for domain-aware decomposition)
# ========================================================================
domain_name: Optional[str]
"""Domain identifier (e.g., 'csx_railway', 'generic'). Default: 'generic'"""

subsystem_id: Optional[str]
"""Subsystem identifier within domain (e.g., 'train_management', 'traffic_control')"""

domain_context: Optional[Dict[str, Any]]
"""Loaded domain context (conventions, glossary, overviews). None for generic mode."""

enable_sectioning: bool
"""Whether to organize requirements into logical sections (Initiation, Completion, etc.)"""

requirement_sections: Optional[Dict[str, List[str]]]
"""Organized requirement IDs by section (e.g., {'Initiation': ['TM-FUNC-001'], ...})"""

requirement_tags: Optional[Dict[str, str]]
"""Requirement type tags (e.g., {'TM-FUNC-001': 'configurable_parameter', 'TM-FUNC-005': 'notification_event'})"""
```

### Modified `DetailedRequirement` Model (src/state.py)

```python
class DetailedRequirement(BaseModel):
    """A detailed, decomposed requirement with traceability."""

    id: str = Field(..., description="Unique requirement ID")
    text: str = Field(..., description="The requirement statement")
    type: RequirementType = Field(..., description="Requirement type")
    parent_id: Optional[str] = Field(None, description="Parent requirement ID for traceability")
    subsystem: str = Field(..., description="Allocated subsystem")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Testable acceptance criteria")
    rationale: Optional[str] = Field(None, description="Why this requirement exists")

    # NEW: Domain-aware tagging
    tags: List[str] = Field(
        default_factory=list,
        description="Requirement tags (e.g., 'configurable_parameter', 'notification_event', 'validation')"
    )
```

### New Field in `QualityMetrics` (src/state.py)

```python
domain_compliance: Optional[float] = Field(
    None,
    ge=0.0,
    le=1.0,
    description="Domain-specific standards compliance (0.0-1.0). None for generic mode."
)
```

**Overall Score Calculation Change**:
- **Generic mode** (4 dimensions): `(completeness + clarity + testability + traceability) / 4`
- **Domain mode** (5 dimensions): `(completeness + clarity + testability + traceability + domain_compliance) / 5`

---

## Implementation Phases

### Phase 1: Domain Context Infrastructure (2-3 days)

#### 1.1 Create Domain Configuration System

**File**: `config/domain_config.py`

```python
"""
Domain configuration registry for project-specific customization.
Enables zero-code-change extensibility for new domains and subsystems.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SubsystemConfig:
    """Configuration for a specific subsystem within a domain."""
    subsystem_id: str
    name: str
    description: str
    overview_file: str  # Relative path within domain_contexts/
    example_files: List[str] = None  # Optional few-shot examples

@dataclass
class DomainConfig:
    """Configuration for a domain (e.g., CSX Railway)."""
    domain_name: str
    description: str

    # Common context files (Layer 1)
    conventions_file: str
    glossary_file: str
    system_overview_file: str

    # Subsystems registry (Layer 2)
    subsystems: Dict[str, SubsystemConfig]

    # Validation settings
    enable_convention_validation: bool = True
    enable_glossary_validation: bool = True
    requirement_template_regex: Optional[str] = None

# ============================================================================
# Domain Registry
# ============================================================================

DOMAIN_REGISTRY: Dict[str, DomainConfig] = {
    "csx_railway": DomainConfig(
        domain_name="csx_railway",
        description="CSX Railway Core System (Train Management, Traffic Control, etc.)",
        conventions_file="common/doc_conventions.md",
        glossary_file="common/glossary.md",
        system_overview_file="common/system_overview.md",
        requirement_template_regex=r"When\s+.+,\s+the\s+\w+\s+shall\s+.+",
        subsystems={
            "train_management": SubsystemConfig(
                subsystem_id="train_management",
                name="Train Management Subsystem",
                description="Manages train data, profiles, sheets, and crew information",
                overview_file="subsystems/train_management/overview.md",
                example_files=["subsystems/train_management/examples/uc_tm_040.md"]
            ),
            "traffic_control": SubsystemConfig(
                subsystem_id="traffic_control",
                name="Traffic Control Subsystem",
                description="Manages signal control, route management, and track authorities",
                overview_file="subsystems/traffic_control/overview.md"
            ),
            "bridge_control": SubsystemConfig(
                subsystem_id="bridge_control",
                name="Bridge Control Subsystem",
                description="Manages bridge operations and safety protocols",
                overview_file="subsystems/bridge_control/overview.md"
            )
        }
    ),
    "generic": DomainConfig(
        domain_name="generic",
        description="Generic mode - no domain-specific context",
        conventions_file=None,
        glossary_file=None,
        system_overview_file=None,
        subsystems={},
        enable_convention_validation=False,
        enable_glossary_validation=False
    )
}

def get_domain_config(domain_name: str) -> DomainConfig:
    """Get domain configuration by name."""
    if domain_name not in DOMAIN_REGISTRY:
        raise ValueError(f"Unknown domain: {domain_name}. Available: {list(DOMAIN_REGISTRY.keys())}")
    return DOMAIN_REGISTRY[domain_name]

def list_available_domains() -> List[str]:
    """List all registered domain names."""
    return list(DOMAIN_REGISTRY.keys())

def list_subsystems(domain_name: str) -> List[str]:
    """List all subsystems for a given domain."""
    config = get_domain_config(domain_name)
    return list(config.subsystems.keys())
```

#### 1.2 Create Domain Loader Utility

**File**: `src/utils/domain_loader.py`

```python
"""
Domain context loading and injection utilities.
Loads domain-specific markdown files and prepares context for LLM prompts.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from functools import lru_cache
import logging

from config.domain_config import DomainConfig, get_domain_config

logger = logging.getLogger(__name__)

class DomainLoadError(Exception):
    """Raised when domain context cannot be loaded."""
    pass

@lru_cache(maxsize=16)
def load_markdown_file(file_path: Path) -> str:
    """Load and cache markdown file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise DomainLoadError(f"Domain context file not found: {file_path}")
    except Exception as e:
        raise DomainLoadError(f"Failed to load domain context from {file_path}: {e}")

def load_domain_context(
    domain_name: str,
    subsystem_id: Optional[str] = None,
    include_examples: bool = False
) -> Dict[str, Any]:
    """
    Load domain context for a given domain and optional subsystem.

    Args:
        domain_name: Domain identifier (e.g., 'csx_railway')
        subsystem_id: Optional subsystem identifier (e.g., 'train_management')
        include_examples: Whether to load example files (few-shot learning)

    Returns:
        Dictionary with loaded domain context:
        {
            'domain_name': str,
            'conventions': str or None,
            'glossary': str or None,
            'system_overview': str or None,
            'subsystem_overview': str or None,
            'examples': List[str] or None,
            'validation_config': {
                'enable_convention_validation': bool,
                'enable_glossary_validation': bool,
                'requirement_template_regex': str or None
            }
        }
    """
    config = get_domain_config(domain_name)
    domain_contexts_dir = Path(__file__).parent.parent.parent / "domain_contexts" / domain_name

    context = {
        'domain_name': domain_name,
        'conventions': None,
        'glossary': None,
        'system_overview': None,
        'subsystem_overview': None,
        'examples': None,
        'validation_config': {
            'enable_convention_validation': config.enable_convention_validation,
            'enable_glossary_validation': config.enable_glossary_validation,
            'requirement_template_regex': config.requirement_template_regex
        }
    }

    # Load Layer 1: Common context (if not generic)
    if config.conventions_file:
        conventions_path = domain_contexts_dir / config.conventions_file
        context['conventions'] = load_markdown_file(conventions_path)
        logger.info(f"Loaded conventions from {conventions_path}")

    if config.glossary_file:
        glossary_path = domain_contexts_dir / config.glossary_file
        context['glossary'] = load_markdown_file(glossary_path)
        logger.info(f"Loaded glossary from {glossary_path}")

    if config.system_overview_file:
        overview_path = domain_contexts_dir / config.system_overview_file
        context['system_overview'] = load_markdown_file(overview_path)
        logger.info(f"Loaded system overview from {overview_path}")

    # Load Layer 2: Subsystem-specific context
    if subsystem_id:
        if subsystem_id not in config.subsystems:
            available = list(config.subsystems.keys())
            raise DomainLoadError(
                f"Unknown subsystem '{subsystem_id}' for domain '{domain_name}'. "
                f"Available: {available}"
            )

        subsystem_config = config.subsystems[subsystem_id]
        subsystem_overview_path = domain_contexts_dir / subsystem_config.overview_file
        context['subsystem_overview'] = load_markdown_file(subsystem_overview_path)
        logger.info(f"Loaded subsystem overview from {subsystem_overview_path}")

        # Load Layer 3: Examples (optional)
        if include_examples and subsystem_config.example_files:
            context['examples'] = []
            for example_file in subsystem_config.example_files:
                example_path = domain_contexts_dir / example_file
                example_content = load_markdown_file(example_path)
                context['examples'].append(example_content)
                logger.info(f"Loaded example from {example_path}")

    return context

def build_domain_prompt_section(context: Dict[str, Any], node_type: str) -> str:
    """
    Build domain context section for LLM prompt based on node type.

    Args:
        context: Loaded domain context dictionary
        node_type: One of 'extract', 'analyze', 'decompose', 'validate'

    Returns:
        Formatted string to inject into LLM prompt
    """
    if context['domain_name'] == 'generic':
        return ""  # No domain context for generic mode

    sections = []

    sections.append("# Domain-Specific Context")
    sections.append(f"Domain: {context['domain_name']}")
    sections.append("")

    # Node-specific context injection
    if node_type == 'extract':
        if context['conventions']:
            sections.append("## Document Conventions")
            sections.append(context['conventions'])
        if context['glossary']:
            sections.append("## Glossary Terms")
            sections.append("The following terms are defined in the project glossary and should be recognized:")
            sections.append(context['glossary'])

    elif node_type == 'analyze':
        if context['system_overview']:
            sections.append("## System Overview")
            sections.append(context['system_overview'])
        if context['subsystem_overview']:
            sections.append("## Target Subsystem Overview")
            sections.append(context['subsystem_overview'])

    elif node_type == 'decompose':
        if context['conventions']:
            sections.append("## Requirement Writing Conventions")
            sections.append("Follow this template for all requirements:")
            sections.append(context['conventions'])
        if context['glossary']:
            sections.append("## Domain Glossary")
            sections.append("Use these terms correctly (capitalize as defined):")
            sections.append(context['glossary'])
        if context['subsystem_overview']:
            sections.append("## Subsystem Context")
            sections.append(context['subsystem_overview'])
        if context['examples']:
            sections.append("## Example Decomposition")
            for i, example in enumerate(context['examples'], 1):
                sections.append(f"### Example {i}")
                sections.append(example)

    elif node_type == 'validate':
        if context['conventions']:
            sections.append("## Requirement Conventions to Validate")
            sections.append(context['conventions'])
        if context['glossary']:
            sections.append("## Glossary for Term Validation")
            sections.append(context['glossary'])

    return "\n".join(sections)
```

#### 1.3 Create Domain Context Markdown Files

**Process**:
1. Create directory structure: `domain_contexts/csx_railway/common/` and `domain_contexts/csx_railway/subsystems/train_management/`
2. Convert extracted .docx content into markdown files:
   - `doc_conventions.md` ← doc_conventions.docx
   - `glossary.md` ← CXC-Core-Glossary.docx
   - `system_overview.md` ← SRS_Core_System_Overview.docx
   - `train_management/overview.md` ← TM_SSRS_Overview.docx
   - `train_management/examples/uc_tm_040.md` ← UC-TM-040 Departure Checklist.docx

**File**: `domain_contexts/csx_railway/common/doc_conventions.md`

```markdown
# Document Conventions for CSX Core System

## Requirement Template Format

All functional requirements must follow this template:

**"When <triggering condition>, the System shall <action> [object] [constraint]."**

### Template Components

- **<triggering condition>**: The event that causes the requirement to activate
  - Example: "When the User selects the delete option"

- **<action>**: What the System must do when triggered
  - Example: "the System shall delete"

- **[object]** (optional): The object upon which the System acts
  - Example: "the record"

- **[constraint]** (optional): Nonfunctional constraint for completion
  - Example: "within 10 ms"

### Full Example

"When the User selects the delete option, the System shall delete the record within 10 ms."

## Modal Verbs

- **shall**: Mandatory requirement (MUST implement)
- **should**: Recommended requirement (SHOULD implement)
- **may**: Optional requirement (MAY implement)
- **must**: Absolute constraint (non-negotiable)

## Capitalization Rules

### Glossary Terms
All terms defined in the CSX Core System Glossary MUST be capitalized when used in requirements.

Examples:
- Train (not train)
- Dispatcher (not dispatcher)
- Control Point (not control point)
- Track Segment (not track segment)
- Authorized User (not authorized user)

### Title Case for Headings
All section titles, requirement titles, and headings use Title Case per APA style:
- Capitalize first word and all major words (4+ letters)
- Lowercase minor words (3 letters or fewer): "and," "the," "for," "in," "of"

## Notation

### Requirement Format in Polarion
Requirements are tracked with:
- **Title**: Summary of requirement (1-2 sentences)
- **Description**: Full requirement text following template
- **Guidance** (optional): Additional context or rationale

### Traceability Fields
- **has parent**: Section within SSRS containing this requirement
- **refines**: SRS requirement that this SSRS requirement traces to
- **relates to**: Related requirements (not direct traceability)

## Prohibited Practices

❌ **Do NOT use vague terms**:
- "fast," "slow," "quickly"
- "user-friendly," "easy"
- "adequate," "sufficient"
- "reasonable," "appropriate"

✅ **Use specific, measurable terms**:
- "within 500ms," "at 95th percentile"
- "with 99.9% uptime," "for 1000 concurrent users"
- "compliant with OAuth 2.0 standard"
```

*(Similar markdown files created for glossary.md, system_overview.md, train_management/overview.md, uc_tm_040.md)*

---

### Phase 2: State Schema Updates (1 day)

#### 2.1 Update `src/state.py`

**Changes**:
1. Add domain context fields to `DecompositionState` TypedDict
2. Add `domain_compliance` field to `QualityMetrics` Pydantic model
3. Update `create_initial_state()` to accept domain parameters
4. Update `overall_score` calculation logic to handle 4 vs 5 dimensions

**Modified `QualityMetrics` model**:

```python
class QualityMetrics(BaseModel):
    """Quality assessment scores and issues."""

    completeness: float = Field(..., ge=0.0, le=1.0)
    clarity: float = Field(..., ge=0.0, le=1.0)
    testability: float = Field(..., ge=0.0, le=1.0)
    traceability: float = Field(..., ge=0.0, le=1.0)
    domain_compliance: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Domain-specific compliance (CSX conventions, glossary). None for generic mode."
    )
    overall_score: float = Field(..., ge=0.0, le=1.0)
    issues: List[QualityIssue] = Field(default_factory=list)

    @field_validator("overall_score")
    @classmethod
    def validate_overall_score(cls, v: float, info) -> float:
        """Calculate overall score based on available dimensions."""
        # If domain_compliance exists, use 5 dimensions, else use 4
        # Note: Actual calculation done in QualityAssuranceAgent
        return v
```

**Modified `DecompositionState` TypedDict**:

```python
class DecompositionState(TypedDict, total=False):
    # ... existing fields ...

    # ========================================================================
    # Domain Context (Phase 7 - Domain Awareness)
    # ========================================================================
    domain_name: str
    """Domain identifier (e.g., 'csx_railway', 'generic'). Default: 'generic'"""

    subsystem_id: Optional[str]
    """Subsystem identifier within domain (e.g., 'train_management')"""

    domain_context: Optional[Dict[str, Any]]
    """Loaded domain context (conventions, glossary, overviews)"""

    enable_sectioning: bool
    """Whether to organize requirements into logical sections"""

    requirement_sections: Optional[Dict[str, List[str]]]
    """Organized requirement IDs by section (Initiation, Completion, etc.)"""
```

**Modified `create_initial_state()` function**:

```python
def create_initial_state(
    spec_document_path: str,
    target_subsystem: str,
    review_before_decompose: bool = False,
    quality_threshold: float = 0.80,
    max_iterations: int = 3,
    domain_name: str = "generic",  # NEW
    subsystem_id: Optional[str] = None,  # NEW
    enable_sectioning: bool = False  # NEW
) -> DecompositionState:
    """Create initial state with optional domain context."""

    # Load domain context if not generic
    domain_context = None
    if domain_name != "generic":
        from src.utils.domain_loader import load_domain_context
        domain_context = load_domain_context(
            domain_name=domain_name,
            subsystem_id=subsystem_id,
            include_examples=True
        )

    return DecompositionState(
        # ... existing fields ...
        domain_name=domain_name,
        subsystem_id=subsystem_id,
        domain_context=domain_context,
        enable_sectioning=enable_sectioning,
        requirement_sections=None
    )
```

---

### Phase 3: Skill Modifications (2-3 days)

#### 3.1 Update `skills/system-analysis/SKILL.md`

**Section to Add** (after line 100):

```markdown
### Step 3.5: Incorporate Domain-Specific Allocation Patterns (If Applicable)

If domain context is provided (e.g., CSX Railway), incorporate domain-specific allocation patterns into your rules.

**Example (CSX Railway - Train Management Subsystem)**:

```
IF requirement involves Dispatcher Bulletin OR Train Sheet management
  THEN allocate to Train Management subsystem

ELSE IF requirement involves signal control OR route clearance
  THEN do NOT allocate (belongs to Traffic Control subsystem)

ELSE IF requirement involves Crew Set OR crew assignment
  THEN allocate to Train Management subsystem

ELSE IF requirement involves Track Circuit OR Control Point
  THEN do NOT allocate (belongs to Infrastructure Management subsystem)
```

**Quality Check for Domain-Aware Rules**:
- ✓ Uses domain glossary terms correctly (capitalized as defined)
- ✓ Respects subsystem boundaries defined in domain overview
- ✓ References domain-specific actors (Dispatcher, Train Crew, etc.)
- ✓ Considers domain-specific interfaces (MIS, PTC BOS, etc.)

---

### Step 3.6: Define Domain-Aware Naming Convention (If Applicable)

If domain context specifies naming conventions, incorporate them:

**CSX Railway Example**:
- Train Management subsystem: `TM-{TYPE}-{NNN}` (e.g., TM-FUNC-001)
- Traffic Control subsystem: `TC-{TYPE}-{NNN}` (e.g., TC-FUNC-001)
- Bridge Control subsystem: `BC-{TYPE}-{NNN}` (e.g., BC-FUNC-001)

**Generic Fallback**:
- Use subsystem acronym: `{SUBSYSTEM_ABBREV}-{TYPE}-{NNN}`
```

#### 3.2 Update `skills/requirements-decomposition/SKILL.md`

**Section to Add** (after line 50):

```markdown
## Domain-Aware Decomposition (If Applicable)

If domain context is provided, ensure decomposed requirements follow domain conventions:

### CSX Railway Conventions

**Requirement Template**:
"When <triggering condition>, the System shall <action> [object] [constraint]."

**Example**:
- ✅ "When an Authorized User initiates the Departure Checklist, the Train Management Subsystem shall display the Job Briefing section and provide an option for the Authorized User to acknowledge."
- ❌ "System shows departure checklist to user."

**Glossary Term Usage**:
- Capitalize all terms defined in glossary: Train, Dispatcher, Control Point, Authorized User
- Use exact terminology from domain glossary (e.g., "Train Sheet" not "train record")

**Subsystem-Specific Patterns**:
- Train Management: Focus on Train data, profiles, sheets, crew management
- Traffic Control: Focus on signal control, route management, track authorities
- Bridge Control: Focus on bridge operations, safety protocols

**Traceability**:
- `parent_id` should reference SRS Use Case ID (e.g., "UC-TM-040")
- `rationale` should explain decomposition from system-level to subsystem-level

---
```

#### 3.3 Update `skills/requirements-quality-validation/SKILL.md`

**New Section to Add** (after line 160, before "Output Format"):

```markdown
---

### 5. Domain Compliance (20%) - **Only for Domain-Aware Mode**

**Definition**: Requirements follow domain-specific conventions, use glossary terms correctly, and comply with project standards.

**Note**: This dimension is ONLY scored when domain context is provided (e.g., CSX Railway). For generic mode, skip this dimension and use 4-dimension scoring.

**Scoring Guidelines** (CSX Railway):
- **1.0 (Excellent)**: All requirements follow template format; all glossary terms capitalized correctly; no convention violations
- **0.8 (Good)**: Minor deviations (1-2 requirements with formatting issues)
- **0.6 (Fair)**: Some requirements violate template; some glossary term errors
- **0.4 (Poor)**: Frequent template violations; many glossary errors
- **0.2 (Very Poor)**: Most requirements ignore conventions
- **0.0 (Unacceptable)**: No attempt to follow domain conventions

**Validation Checks** (CSX Railway):
- [ ] Requirement text follows template: "When <trigger>, System shall <action> [object] [constraint]"
- [ ] All glossary terms are capitalized (Train, Dispatcher, Control Point, Track Segment, etc.)
- [ ] No vague terms ("fast", "user-friendly", "adequate", "reasonable")
- [ ] Modal verbs used correctly (shall, should, may, must)
- [ ] Subsystem name matches domain conventions (e.g., "Train Management Subsystem")

**Examples**:

**Good Domain Compliance (Score: 1.0)** (CSX Railway):
```
TM-FUNC-001: When an Authorized User initiates the Departure Checklist,
the Train Management Subsystem shall display the Job Briefing section and
provide an option for the Authorized User to acknowledge.

✓ Follows template format
✓ Capitalizes "Authorized User," "Departure Checklist," "Job Briefing"
✓ Uses "shall" correctly
✓ Specific and measurable
```

**Poor Domain Compliance (Score: 0.4)** (CSX Railway):
```
TM-FUNC-001: The system shows the departure checklist to the user quickly.

❌ Does not follow template (missing "When <trigger>")
❌ "departure checklist" not capitalized (should be "Departure Checklist")
❌ "user" not capitalized (should be "Authorized User")
❌ Vague term "quickly" (violates conventions)
```

---

## Overall Score Calculation

### 4-Dimension Scoring (Generic Mode)
```
overall_score = (completeness + clarity + testability + traceability) / 4
```

### 5-Dimension Scoring (Domain-Aware Mode)
```
overall_score = (completeness + clarity + testability + traceability + domain_compliance) / 5
```

---
```

---

### Phase 4: Validation Enhancements (2-3 days)

#### 4.1 Implement Domain Compliance Validation

**File**: `src/agents/quality_assurance.py`

**New Methods to Add**:

```python
def _validate_domain_compliance(
    self,
    requirements: List[DetailedRequirement],
    domain_context: Dict[str, Any]
) -> Tuple[float, List[QualityIssue]]:
    """
    Validate domain-specific compliance (5th quality dimension).

    Returns:
        Tuple of (compliance_score, issues_list)
    """
    if not domain_context or domain_context.get('domain_name') == 'generic':
        return None, []  # Skip for generic mode

    validation_config = domain_context['validation_config']
    issues = []

    # Check 1: Requirement template format (if regex provided)
    if validation_config['requirement_template_regex']:
        import re
        template_regex = re.compile(validation_config['requirement_template_regex'], re.IGNORECASE)

        non_compliant = []
        for req in requirements:
            if not template_regex.search(req.text):
                non_compliant.append(req.id)
                issues.append(QualityIssue(
                    severity=QualitySeverity.MAJOR,
                    requirement_id=req.id,
                    dimension="domain_compliance",
                    description=f"Requirement does not follow domain template format",
                    suggestion="Rewrite using: 'When <trigger>, the System shall <action> [object] [constraint]'"
                ))

    # Check 2: Glossary term capitalization (if glossary provided)
    if validation_config['enable_glossary_validation'] and domain_context.get('glossary'):
        glossary_terms = self._extract_glossary_terms(domain_context['glossary'])

        for req in requirements:
            # Find terms that should be capitalized but aren't
            for term in glossary_terms:
                # Check for lowercase usage of capitalized terms
                lowercase_pattern = re.compile(r'\b' + re.escape(term.lower()) + r'\b')
                if lowercase_pattern.search(req.text) and term not in req.text:
                    issues.append(QualityIssue(
                        severity=QualitySeverity.MINOR,
                        requirement_id=req.id,
                        dimension="domain_compliance",
                        description=f"Glossary term '{term}' should be capitalized",
                        suggestion=f"Replace '{term.lower()}' with '{term}'"
                    ))

    # Calculate score based on issues
    total_checks = len(requirements) * 2  # Template + glossary per requirement
    violations = len(issues)
    compliance_score = max(0.0, 1.0 - (violations / total_checks))

    return compliance_score, issues

def _extract_glossary_terms(self, glossary_text: str) -> List[str]:
    """Extract list of glossary terms that should be capitalized."""
    # Parse glossary markdown and extract capitalized terms
    # Implementation depends on glossary format
    terms = []
    # Simple implementation: extract terms after "**" markers
    import re
    pattern = re.compile(r'\*\*([A-Z][A-Za-z\s]+)\*\*')
    matches = pattern.findall(glossary_text)
    terms.extend(matches)
    return terms
```

**Modified `validate()` method**:

```python
def validate(
    self,
    requirements: List[DetailedRequirement],
    strategy: DecompositionStrategy,
    domain_context: Optional[Dict[str, Any]] = None
) -> QualityMetrics:
    """
    Validate requirements quality with optional domain compliance.

    Args:
        requirements: Decomposed requirements to validate
        strategy: Decomposition strategy (for context)
        domain_context: Optional domain context for compliance checking

    Returns:
        QualityMetrics with 4 or 5 dimensions depending on domain context
    """
    # Existing validation for 4 dimensions
    completeness_score, completeness_issues = self._validate_completeness(requirements)
    clarity_score, clarity_issues = self._validate_clarity(requirements)
    testability_score, testability_issues = self._validate_testability(requirements, strategy)
    traceability_score, traceability_issues = self._validate_traceability(requirements, strategy)

    # Domain compliance (5th dimension) - only if domain context provided
    domain_compliance_score = None
    domain_issues = []
    if domain_context and domain_context.get('domain_name') != 'generic':
        domain_compliance_score, domain_issues = self._validate_domain_compliance(
            requirements, domain_context
        )

    # Calculate overall score (4 or 5 dimensions)
    if domain_compliance_score is not None:
        overall_score = (
            completeness_score + clarity_score + testability_score +
            traceability_score + domain_compliance_score
        ) / 5.0
    else:
        overall_score = (
            completeness_score + clarity_score + testability_score + traceability_score
        ) / 4.0

    # Combine all issues
    all_issues = completeness_issues + clarity_issues + testability_issues + traceability_issues + domain_issues

    return QualityMetrics(
        completeness=completeness_score,
        clarity=clarity_score,
        testability=testability_score,
        traceability=traceability_score,
        domain_compliance=domain_compliance_score,
        overall_score=overall_score,
        issues=all_issues
    )
```

#### 4.2 Inject Domain Context into Agent Prompts

**Files to Modify**:
- `src/agents/requirements_analyst.py` (extract node)
- `src/agents/system_architect.py` (analyze node)
- `src/agents/requirements_engineer.py` (decompose node)
- `src/agents/quality_assurance.py` (validate node)

**Pattern for Each Agent** (example for `requirements_analyst.py`):

```python
def extract_requirements(
    self,
    document_text: str,
    domain_context: Optional[Dict[str, Any]] = None
) -> List[Requirement]:
    """Extract requirements with optional domain context."""

    # Build domain-aware prompt
    from src.utils.domain_loader import build_domain_prompt_section
    domain_section = build_domain_prompt_section(domain_context, node_type='extract') if domain_context else ""

    system_prompt = f"""You are a requirements extraction expert...

{self.get_skill_content()}

{domain_section}

IMPORTANT: Return ONLY a valid JSON array..."""

    # Rest of extraction logic...
```

---

### Phase 5: Requirement Sectioning (1-2 days)

#### 5.1 Implement Post-Processing Sectioner

**File**: `src/utils/requirement_sectioner.py`

```python
"""
Requirement sectioning utility for organizing decomposed requirements into logical groups.
Implements pattern-based identification of requirement sections (Initiation, Completion, etc.).
"""

from typing import List, Dict
import re
from src.state import DetailedRequirement

# Section patterns based on CSX benchmark (UC-TM-040)
SECTION_PATTERNS = {
    "Initiation": [
        r"initiat(e|ion|ing)",
        r"enable.*option",
        r"provide.*option.*initiate",
        r"start",
        r"begin"
    ],
    "Configuration": [
        r"configur(e|able|ation)",
        r"parameter",
        r"Boolean.*control",
        r"visibility"
    ],
    "Display": [
        r"display",
        r"show",
        r"present",
        r"render"
    ],
    "Validation": [
        r"validat(e|ion)",
        r"verify",
        r"check",
        r"confirm"
    ],
    "Processing": [
        r"process",
        r"calculat(e|ion)",
        r"transform",
        r"apply"
    ],
    "Completion": [
        r"complet(e|ion)",
        r"finish",
        r"save.*complete",
        r"proceed.*completion"
    ],
    "Events": [
        r"generat(e|ion).*event",
        r"EV-",
        r"notif(y|ication)",
        r"trigger.*event"
    ],
    "Error Handling": [
        r"error",
        r"failure",
        r"exception",
        r"mismatch",
        r"prevent.*complet"
    ]
}

# Tag patterns for special requirement types (CSX Railway)
TAG_PATTERNS = {
    "configurable_parameter": [
        r"CFG-",
        r"configurable\s+parameter",
        r"Boolean\s+configuration\s+parameter"
    ],
    "notification_event": [
        r"EV-",
        r"generate.*event",
        r"notification\s+event"
    ],
    "validation": [
        r"validat(e|ion)",
        r"verify",
        r"check.*match"
    ],
    "error_handling": [
        r"error",
        r"failure",
        r"mismatch"
    ]
}

def tag_requirements(
    requirements: List[DetailedRequirement],
    use_default_patterns: bool = True
) -> List[DetailedRequirement]:
    """
    Tag requirements based on text patterns (e.g., 'configurable_parameter', 'notification_event').
    Modifies requirements in-place by adding tags.

    Args:
        requirements: List of decomposed requirements
        use_default_patterns: Whether to use default CSX-style patterns

    Returns:
        List of requirements with tags added
    """
    for req in requirements:
        req_text = req.text
        req_id = req.id
        req.tags = []  # Initialize tags list

        # Check for special requirement types
        for tag_name, patterns in TAG_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, req_text, re.IGNORECASE) or re.search(pattern, req_id):
                    if tag_name not in req.tags:
                        req.tags.append(tag_name)
                    break

    return requirements

def section_requirements(
    requirements: List[DetailedRequirement],
    use_default_patterns: bool = True
) -> Dict[str, List[str]]:
    """
    Organize requirements into logical sections based on text patterns.

    Args:
        requirements: List of decomposed requirements
        use_default_patterns: Whether to use default CSX-style patterns

    Returns:
        Dictionary mapping section names to requirement IDs
        Example: {'Initiation': ['TM-FUNC-001', 'TM-FUNC-002'], ...}
    """
    sections: Dict[str, List[str]] = {section: [] for section in SECTION_PATTERNS.keys()}
    sections["Other"] = []  # Catch-all for unmatched requirements

    for req in requirements:
        matched = False
        req_text_lower = req.text.lower()

        # Try to match requirement to a section
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, req_text_lower):
                    sections[section_name].append(req.id)
                    matched = True
                    break
            if matched:
                break

        if not matched:
            sections["Other"].append(req.id)

    # Remove empty sections
    sections = {k: v for k, v in sections.items() if v}

    return sections

def format_sectioned_output(
    requirements: List[DetailedRequirement],
    sections: Dict[str, List[str]]
) -> str:
    """
    Format sectioned requirements for output (markdown format).

    Returns:
        Markdown-formatted string with requirements organized by section
    """
    output_lines = []
    output_lines.append("# Decomposed Requirements (Organized by Section)\n")

    for section_name, req_ids in sections.items():
        output_lines.append(f"## {section_name}\n")

        for req_id in req_ids:
            req = next((r for r in requirements if r.id == req_id), None)
            if req:
                # Display tags as badges
                tags_str = ""
                if req.tags:
                    tags_str = " " + " ".join([f"`{tag}`" for tag in req.tags])

                output_lines.append(f"### {req.id}: {req.type.value}{tags_str}\n")
                output_lines.append(f"**Text**: {req.text}\n")
                if req.parent_id:
                    output_lines.append(f"**Parent**: {req.parent_id}\n")
                if req.rationale:
                    output_lines.append(f"**Rationale**: {req.rationale}\n")
                if req.acceptance_criteria:
                    output_lines.append("**Acceptance Criteria**:\n")
                    for criterion in req.acceptance_criteria:
                        output_lines.append(f"  - {criterion}\n")
                output_lines.append("\n")

    return "\n".join(output_lines)
```

#### 5.2 Integrate Sectioning into Workflow

**File**: `src/workflow.py` (or main workflow file)

**Add new node or modify output node**:

```python
def section_requirements_node(state: DecompositionState) -> DecompositionState:
    """
    Optional node to section requirements into logical groups and tag special types.
    Only runs if enable_sectioning flag is True.
    """
    if not state.get("enable_sectioning", False):
        return state  # Skip sectioning

    from src.utils.requirement_sectioner import section_requirements, tag_requirements
    from src.state import DetailedRequirement

    # Deserialize requirements
    requirements = [
        DetailedRequirement(**req_dict)
        for req_dict in state["decomposed_requirements"]
    ]

    # Tag requirements (configurable_parameter, notification_event, etc.)
    tagged_requirements = tag_requirements(requirements, use_default_patterns=True)

    # Section requirements
    sections = section_requirements(tagged_requirements, use_default_patterns=True)

    # Serialize back to state
    serialized_reqs = [req.dict() for req in tagged_requirements]

    return {
        **state,
        "decomposed_requirements": serialized_reqs,
        "requirement_sections": sections
    }
```

---

### Phase 6: CLI and Integration (1-2 days)

#### 6.1 Update CLI Arguments

**File**: `main.py` (or CLI entry point)

**Add new arguments**:

```python
parser.add_argument(
    "--domain",
    type=str,
    default="generic",
    help="Domain name (e.g., 'csx_railway', 'generic'). Default: generic"
)

parser.add_argument(
    "--subsystem-id",
    type=str,
    default=None,
    help="Subsystem identifier within domain (e.g., 'train_management'). Required if domain != generic."
)

parser.add_argument(
    "--enable-sectioning",
    action="store_true",
    help="Organize requirements into logical sections (Initiation, Completion, etc.)"
)

parser.add_argument(
    "--list-domains",
    action="store_true",
    help="List all available domains and exit"
)

parser.add_argument(
    "--list-subsystems",
    type=str,
    metavar="DOMAIN",
    help="List all subsystems for specified domain and exit"
)
```

**Add domain listing commands**:

```python
if args.list_domains:
    from config.domain_config import list_available_domains
    domains = list_available_domains()
    print("Available domains:")
    for domain in domains:
        print(f"  - {domain}")
    sys.exit(0)

if args.list_subsystems:
    from config.domain_config import list_subsystems
    subsystems = list_subsystems(args.list_subsystems)
    print(f"Subsystems for domain '{args.list_subsystems}':")
    for subsystem in subsystems:
        print(f"  - {subsystem}")
    sys.exit(0)
```

#### 6.2 Usage Examples

**Generic Mode (no changes)**:
```bash
python main.py spec.txt --subsystem "Power Management"
```

**CSX Mode with Train Management**:
```bash
python main.py Staging_Area/SRS_Use_Case_40.docx \
    --subsystem "Train Management" \
    --domain csx_railway \
    --subsystem-id train_management \
    --enable-sectioning
```

**List Available Domains**:
```bash
python main.py --list-domains
# Output:
# Available domains:
#   - csx_railway
#   - generic
```

**List Subsystems**:
```bash
python main.py --list-subsystems csx_railway
# Output:
# Subsystems for domain 'csx_railway':
#   - train_management
#   - traffic_control
#   - bridge_control
```

---

### Phase 7: Testing and Validation (2-3 days)

#### 7.1 Unit Tests for Domain Context

**File**: `tests/unit/test_domain_loader.py`

```python
import pytest
from src.utils.domain_loader import load_domain_context, DomainLoadError

def test_load_generic_domain():
    """Test loading generic (no domain context) mode."""
    context = load_domain_context(domain_name="generic")
    assert context['domain_name'] == 'generic'
    assert context['conventions'] is None
    assert context['glossary'] is None

def test_load_csx_railway_common():
    """Test loading CSX Railway common context."""
    context = load_domain_context(domain_name="csx_railway")
    assert context['domain_name'] == 'csx_railway'
    assert context['conventions'] is not None
    assert context['glossary'] is not None
    assert 'When <triggering condition>' in context['conventions']

def test_load_csx_railway_train_management():
    """Test loading CSX Railway Train Management subsystem."""
    context = load_domain_context(
        domain_name="csx_railway",
        subsystem_id="train_management"
    )
    assert context['subsystem_overview'] is not None
    assert 'Train Management Subsystem' in context['subsystem_overview']

def test_unknown_domain():
    """Test error handling for unknown domain."""
    with pytest.raises(DomainLoadError, match="Unknown domain"):
        load_domain_context(domain_name="nonexistent_domain")

def test_unknown_subsystem():
    """Test error handling for unknown subsystem."""
    with pytest.raises(DomainLoadError, match="Unknown subsystem"):
        load_domain_context(
            domain_name="csx_railway",
            subsystem_id="nonexistent_subsystem"
        )
```

#### 7.2 Integration Test with UC-TM-040

**File**: `tests/integration/test_csx_train_management.py`

```python
import pytest
from pathlib import Path
from src.state import create_initial_state
from src.workflow import run_decomposition_workflow

@pytest.mark.integration
def test_uc_tm_040_decomposition():
    """
    Integration test: Decompose UC-TM-040 (Train Departure Checklist)
    for Train Management subsystem with CSX domain context.

    Expected:
    - Quality score >= 0.80
    - Domain compliance score >= 0.80
    - Requirements follow CSX template format
    - Glossary terms capitalized correctly
    - Requirements organized into sections
    """
    spec_path = Path("Staging_Area/SRS_Use_Case_40.docx")

    # Create initial state with CSX domain context
    initial_state = create_initial_state(
        spec_document_path=str(spec_path),
        target_subsystem="Train Management",
        domain_name="csx_railway",
        subsystem_id="train_management",
        enable_sectioning=True,
        quality_threshold=0.80
    )

    # Run workflow
    final_state = run_decomposition_workflow(initial_state)

    # Assertions
    assert final_state["validation_passed"] is True, "Quality validation should pass"

    quality_metrics = final_state["quality_metrics"]
    assert quality_metrics["overall_score"] >= 0.80, "Overall quality score should be >= 0.80"
    assert quality_metrics["domain_compliance"] is not None, "Domain compliance should be scored"
    assert quality_metrics["domain_compliance"] >= 0.80, "Domain compliance should be >= 0.80"

    # Check requirement format
    decomposed_reqs = final_state["decomposed_requirements"]
    assert len(decomposed_reqs) > 0, "Should have decomposed requirements"

    for req in decomposed_reqs:
        # Check ID format (TM-{TYPE}-{NNN})
        assert req["id"].startswith("TM-"), f"Requirement ID should start with 'TM-': {req['id']}"

        # Check template format (basic check)
        assert "shall" in req["text"].lower(), f"Requirement should use 'shall': {req['text']}"

    # Check sectioning
    assert final_state["requirement_sections"] is not None, "Requirements should be sectioned"
    sections = final_state["requirement_sections"]
    assert len(sections) > 0, "Should have at least one section"

    # Expected sections for departure checklist
    expected_sections = ["Initiation", "Validation", "Completion"]
    for expected_section in expected_sections:
        assert expected_section in sections, f"Should have '{expected_section}' section"

@pytest.mark.integration
def test_benchmark_comparison():
    """
    Compare decomposition output with benchmark (UC-TM-040 Departure Checklist.docx).

    This is a manual validation test - outputs comparison report for human review.
    """
    # Run decomposition
    spec_path = Path("Staging_Area/SRS_Use_Case_40.docx")
    initial_state = create_initial_state(
        spec_document_path=str(spec_path),
        target_subsystem="Train Management",
        domain_name="csx_railway",
        subsystem_id="train_management",
        enable_sectioning=True
    )

    final_state = run_decomposition_workflow(initial_state)

    # Load benchmark
    benchmark_path = Path("Staging_Area/UC-TM-040 Departure Checklist.docx")
    # Parse benchmark and compare (implementation depends on benchmark format)

    # Generate comparison report
    report_path = Path("test_output/uc_tm_040_comparison.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        f.write("# UC-TM-040 Decomposition vs Benchmark Comparison\n\n")
        f.write("## System Output\n\n")
        # Write decomposed requirements
        for req in final_state["decomposed_requirements"]:
            f.write(f"### {req['id']}\n")
            f.write(f"{req['text']}\n\n")

        f.write("## Benchmark Requirements\n\n")
        f.write("(See: Staging_Area/UC-TM-040 Departure Checklist.docx)\n\n")

        f.write("## Quality Metrics\n\n")
        metrics = final_state["quality_metrics"]
        f.write(f"- Overall Score: {metrics['overall_score']:.2f}\n")
        f.write(f"- Completeness: {metrics['completeness']:.2f}\n")
        f.write(f"- Clarity: {metrics['clarity']:.2f}\n")
        f.write(f"- Testability: {metrics['testability']:.2f}\n")
        f.write(f"- Traceability: {metrics['traceability']:.2f}\n")
        f.write(f"- Domain Compliance: {metrics['domain_compliance']:.2f}\n")

    print(f"Comparison report written to: {report_path}")
```

#### 7.3 Manual Validation Steps

1. **Run decomposition on UC-TM-040**:
   ```bash
   python main.py Staging_Area/SRS_Use_Case_40.docx \
       --subsystem "Train Management" \
       --domain csx_railway \
       --subsystem-id train_management \
       --enable-sectioning \
       --output uc_tm_040_output.json
   ```

2. **Compare output with benchmark** (`Staging_Area/UC-TM-040 Departure Checklist.docx`):
   - Requirement coverage (all features covered?)
   - Requirement format (follows CSX template?)
   - Glossary term usage (capitalized correctly?)
   - Logical flow (Initiation → Processing → Completion?)
   - Configurable parameters (identified correctly?)
   - Notification events (identified correctly?)

3. **Quality gate validation**:
   - Overall score >= 0.80?
   - Domain compliance score >= 0.80?
   - All quality issues addressed?

---

## Critical Files to Modify

### New Files to Create

| File Path | Purpose | Size Estimate |
|-----------|---------|---------------|
| `config/domain_config.py` | Domain registry and configuration | ~200 lines |
| `src/utils/domain_loader.py` | Domain context loading utilities | ~150 lines |
| `src/utils/requirement_sectioner.py` | Requirement sectioning and tagging logic | ~150 lines |
| `domain_contexts/csx_railway/common/doc_conventions.md` | CSX conventions | ~100 lines |
| `domain_contexts/csx_railway/common/glossary.md` | CSX glossary | ~200 lines |
| `domain_contexts/csx_railway/common/system_overview.md` | SRS overview | ~150 lines |
| `domain_contexts/csx_railway/subsystems/train_management/overview.md` | TM overview | ~50 lines |
| `domain_contexts/csx_railway/subsystems/train_management/examples/uc_tm_040.md` | UC-TM-040 benchmark | ~200 lines |
| `tests/unit/test_domain_loader.py` | Unit tests for domain loading | ~100 lines |
| `tests/integration/test_csx_train_management.py` | Integration test for UC-TM-040 | ~150 lines |

### Existing Files to Modify

| File Path | Changes Required | Estimated Impact |
|-----------|------------------|------------------|
| `src/state.py` | Add domain context fields (lines 275-290) | ~25 lines added |
| `src/state.py` | Add `tags` field to `DetailedRequirement` (line 147) | ~5 lines added |
| `src/state.py` | Add `domain_compliance` to `QualityMetrics` (line 191) | ~8 lines added |
| `src/state.py` | Update `create_initial_state()` (lines 396-437) | ~20 lines modified |
| `src/agents/requirements_analyst.py` | Add domain context parameter + injection | ~15 lines modified |
| `src/agents/system_architect.py` | Add domain context parameter + injection | ~15 lines modified |
| `src/agents/requirements_engineer.py` | Add domain context parameter + injection | ~15 lines modified |
| `src/agents/quality_assurance.py` | Add `_validate_domain_compliance()` method | ~80 lines added |
| `src/agents/quality_assurance.py` | Update `validate()` method for 5th dimension | ~20 lines modified |
| `skills/system-analysis/SKILL.md` | Add domain-aware allocation patterns (after line 100) | ~40 lines added |
| `skills/requirements-decomposition/SKILL.md` | Add domain-aware conventions (after line 50) | ~50 lines added |
| `skills/requirements-quality-validation/SKILL.md` | Add 5th dimension section (after line 160) | ~80 lines added |
| `main.py` | Add CLI arguments for domain context | ~40 lines added |
| `src/workflow.py` | Add `section_requirements_node()` (optional) | ~30 lines added |

---

## Validation Criteria

### Success Metrics for UC-TM-040 Decomposition

1. **Quality Gate**: Overall score >= 0.80
2. **Domain Compliance**: Domain compliance score >= 0.80
3. **Template Compliance**: >= 90% of requirements follow CSX template format
4. **Glossary Compliance**: >= 95% of glossary terms capitalized correctly
5. **Coverage**: All features from UC-TM-040 represented in decomposed requirements
6. **Logical Flow**: Requirements organized into logical sections (Initiation, Completion, etc.)
7. **Traceability**: All requirements have `parent_id` referencing UC-TM-040

### Benchmark Comparison Checklist

Compare system output with `Staging_Area/UC-TM-040 Departure Checklist.docx`:

- [ ] All departure checklist features covered (Job Briefing, Work Locations, Train Consist, PTC, Dispatcher Bulletin)
- [ ] Configurable parameters identified and tagged (CFG-TM.CHECKLIST.* parameters with `configurable_parameter` tag)
- [ ] Notification events identified and tagged (EV-TM.DEPARTURE.CHECKLIST.* events with `notification_event` tag)
- [ ] Requirement IDs follow TM-{TYPE}-{NNN} format
- [ ] Requirements organized into logical sections
- [ ] Tags displayed correctly in output (e.g., `TM-FUNC-001: FUNC `configurable_parameter``)
- [ ] No critical quality issues
- [ ] Human-readable output suitable for stakeholder review

---

## Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1**: Domain Context Infrastructure | 2-3 days | Domain config, loader, markdown files |
| **Phase 2**: State Schema Updates | 1 day | Updated state.py with domain fields |
| **Phase 3**: Skill Modifications | 2-3 days | Updated SKILL.md files with CSX examples |
| **Phase 4**: Validation Enhancements | 2-3 days | Domain compliance validation, 5th dimension |
| **Phase 5**: Requirement Sectioning | 1-2 days | Sectioner utility, integration |
| **Phase 6**: CLI and Integration | 1-2 days | CLI arguments, usage examples |
| **Phase 7**: Testing and Validation | 2-3 days | Unit tests, integration tests, UC-TM-040 validation |
| **Total** | **10-14 days** | Fully functional domain-aware system |

---

## Extensibility for Future Subsystems

### Adding a New CSX Subsystem (e.g., Traffic Control)

**Steps** (zero code changes required):

1. **Create subsystem overview**: `domain_contexts/csx_railway/subsystems/traffic_control/overview.md`
2. **Register in config**: Add entry to `DOMAIN_REGISTRY['csx_railway'].subsystems` in `config/domain_config.py`
3. **Optional examples**: Add example decompositions to `subsystems/traffic_control/examples/`

**Usage**:
```bash
python main.py SRS_Traffic_Control.docx \
    --subsystem "Traffic Control" \
    --domain csx_railway \
    --subsystem-id traffic_control \
    --enable-sectioning
```

### Adding a New Domain (e.g., Aerospace)

**Steps**:

1. **Create domain structure**: `domain_contexts/aerospace/common/` and `domain_contexts/aerospace/subsystems/`
2. **Create context files**: conventions.md, glossary.md, system_overview.md
3. **Register domain**: Add entry to `DOMAIN_REGISTRY` in `config/domain_config.py`
4. **Optional: Custom validation**: Implement aerospace-specific validation patterns if needed

**No code changes required** - only configuration and markdown files.

---

## Risk Mitigation

### Risk 1: LLM Not Following Domain Conventions

**Mitigation**:
- Explicit examples in skills (good vs bad requirements)
- Domain context injected at every node
- Automated validation catches violations
- Iterative refinement loop enforces corrections

### Risk 2: Glossary Term Extraction Complexity

**Mitigation**:
- Start with simple regex-based extraction from markdown
- Glossary format standardized (markdown with `**Term**` pattern)
- Manual glossary curation to ensure quality
- False positives handled gracefully (MINOR severity)

### Risk 3: Section Identification Accuracy

**Mitigation**:
- Pattern-based approach with multiple regex patterns per section
- "Other" catch-all section for unmatched requirements
- Manual review option for sectioning output
- Sectioning is optional (--enable-sectioning flag)

### Risk 4: Breaking Existing Generic Functionality

**Mitigation**:
- Backward compatibility enforced: generic mode unchanged
- Domain context is optional (default: "generic")
- All domain-specific code paths check for domain context presence
- Existing tests remain valid and passing

---

## Post-Implementation Tasks

1. **Documentation Updates**:
   - Update `README.md` with domain-aware usage examples
   - Update `docs/user_guide.md` with CSX Railway section
   - Create `docs/domain_guide.md` explaining how to add new domains/subsystems
   - Update `CLAUDE.md` with Phase 7 achievements

2. **User Training**:
   - Create tutorial for CSX users: "Decomposing Requirements for Train Management"
   - Document benchmark comparison process
   - Provide troubleshooting guide for domain validation issues

3. **Monitoring**:
   - Track domain compliance scores across multiple runs
   - Identify common convention violations for skill refinement
   - Collect feedback on sectioning accuracy

---

## Summary

This implementation plan provides a **flexible, extensible architecture** for domain-aware requirements decomposition that:

✅ Maintains backward compatibility with generic mode
✅ Enables zero-code-change extensibility for new subsystems
✅ Adds CSX Railway domain knowledge without hardcoding
✅ Enhances quality validation with domain compliance dimension
✅ Organizes requirements into logical sections
✅ Validates against benchmark (UC-TM-040)
✅ Supports multiple domains (CSX Railway, future aerospace, automotive, etc.)

The 3-tier domain context architecture (Common → Subsystem-Specific → Examples) provides the flexibility needed for different CSX subsystems (Train Management, Traffic Control, Bridge Control) while keeping the core system generic and reusable.
