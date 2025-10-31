"""
Phase 0: Skills Validation Test Suite

Tests whether SKILL.md files can reliably guide LLM behavior.
"""

import json
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

def load_skill(skill_name: str) -> str:
    """Load skill content from markdown file."""
    skill_path = Path(f"skills/{skill_name}/SKILL.md")
    return skill_path.read_text()

def load_spec(spec_name: str) -> str:
    """Load test specification."""
    spec_path = Path(f"examples/{spec_name}.txt")
    return spec_path.read_text()

def load_expected(spec_name: str) -> List[Dict]:
    """Load expected extraction results."""
    # Replace _spec with _expected in the spec name
    expected_name = spec_name.replace("_spec", "_expected")
    expected_path = Path(f"examples/{expected_name}.json")
    return json.loads(expected_path.read_text())

def extract_with_skill(spec_text: str, skill_content: str) -> List[Dict]:
    """Extract requirements using skill-guided LLM."""

    # Primary model: Claude Sonnet 4.5 (recommended for Phase 0)
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0.0,
        max_tokens=8192
    )

    # Alternative: OpenAI GPT-4o (uncomment to use)
    # llm = ChatOpenAI(
    #     model="gpt-4o",
    #     temperature=0.0,
    #     max_tokens=8192
    # )

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{skill_content}\n\nApply this methodology to extract requirements."),
        ("human", f"Specification document:\n\n{spec_text}\n\nExtract all requirements as JSON array.")
    ])

    chain = prompt | llm
    response = chain.invoke({})

    # Parse JSON from response
    content = response.content
    if "```json" in content:
        json_text = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        json_text = content.split("```")[1].split("```")[0].strip()
    else:
        json_text = content.strip()

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"\n⚠️  JSON Parse Error: {e}")
        print(f"First 500 chars of response:\n{content[:500]}...")
        print(f"Last 200 chars:\n...{content[-200:]}")
        # Return empty list on parse failure
        return []

def extract_without_skill(spec_text: str) -> List[Dict]:
    """Extract requirements using baseline prompt (no skill)."""

    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0.0,
        max_tokens=8192
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a requirements analyst. Extract all requirements from the specification."),
        ("human", f"Specification:\n\n{spec_text}\n\nExtract requirements as JSON array with fields: id, text, type, source_reference.")
    ])

    chain = prompt | llm
    response = chain.invoke({})

    content = response.content
    if "```json" in content:
        json_text = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        json_text = content.split("```")[1].split("```")[0].strip()
    else:
        json_text = content.strip()

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"\n⚠️  JSON Parse Error: {e}")
        print(f"First 500 chars of response:\n{content[:500]}...")
        print(f"Last 200 chars:\n...{content[-200:]}")
        # Return empty list on parse failure
        return []

def normalize_text(text: str) -> str:
    """Normalize text for fuzzy comparison by removing punctuation and extra whitespace."""
    import re
    # Remove punctuation except for essential characters
    text = re.sub(r'[^\w\s\-/<>=]', '', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.lower().strip()

def calculate_precision_recall(extracted: List[Dict], expected: List[Dict]) -> Dict:
    """Calculate precision and recall metrics using fuzzy text matching."""

    # Normalize texts for fuzzy comparison
    extracted_texts = {normalize_text(req["text"]) for req in extracted if "text" in req}
    expected_texts = {normalize_text(req["text"]) for req in expected if "text" in req}

    true_positives = len(extracted_texts & expected_texts)
    false_positives = len(extracted_texts - expected_texts)
    false_negatives = len(expected_texts - extracted_texts)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }

def test_consistency(spec_text: str, skill_content: str, runs: int = 3) -> float:
    """Test output consistency across multiple runs."""

    results = []
    for i in range(runs):
        extracted = extract_with_skill(spec_text, skill_content)
        # Normalize texts using same function as precision/recall calculation
        result_texts = sorted([normalize_text(req["text"]) for req in extracted if "text" in req])
        results.append(result_texts)

    # Calculate pairwise agreement
    total_agreements = 0
    comparisons = 0

    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            set_i = set(results[i])
            set_j = set(results[j])
            agreement = len(set_i & set_j) / len(set_i | set_j) if len(set_i | set_j) > 0 else 0
            total_agreements += agreement
            comparisons += 1

    consistency = total_agreements / comparisons if comparisons > 0 else 0
    return consistency

def run_phase0_validation():
    """Run complete Phase 0 validation suite."""

    print("="*80)
    print("PHASE 0: SKILLS ARCHITECTURE VALIDATION")
    print("="*80)

    skill_content = load_skill("requirements-extraction")

    results = {}

    for spec_name in ["phase0_simple_spec", "phase0_medium_spec", "phase0_complex_spec"]:
        print(f"\n--- Testing: {spec_name} ---")

        spec_text = load_spec(spec_name)
        expected = load_expected(spec_name)

        # Test with skill
        print("Extracting WITH skill...")
        extracted_with_skill = extract_with_skill(spec_text, skill_content)
        metrics_with_skill = calculate_precision_recall(extracted_with_skill, expected)

        # Test without skill (baseline)
        print("Extracting WITHOUT skill (baseline)...")
        extracted_without_skill = extract_without_skill(spec_text)
        metrics_without_skill = calculate_precision_recall(extracted_without_skill, expected)

        # Test consistency
        print("Testing consistency (3 runs)...")
        consistency = test_consistency(spec_text, skill_content, runs=3)

        # Calculate improvement
        improvement = ((metrics_with_skill["f1"] - metrics_without_skill["f1"]) / metrics_without_skill["f1"] * 100) if metrics_without_skill["f1"] > 0 else 0

        results[spec_name] = {
            "with_skill": metrics_with_skill,
            "without_skill": metrics_without_skill,
            "improvement_percent": improvement,
            "consistency": consistency
        }

        # Print results
        print(f"\nResults for {spec_name}:")
        print(f"  WITH Skill    - Precision: {metrics_with_skill['precision']:.2f}, Recall: {metrics_with_skill['recall']:.2f}, F1: {metrics_with_skill['f1']:.2f}")
        print(f"  WITHOUT Skill - Precision: {metrics_without_skill['precision']:.2f}, Recall: {metrics_without_skill['recall']:.2f}, F1: {metrics_without_skill['f1']:.2f}")
        print(f"  Improvement: {improvement:.1f}%")
        print(f"  Consistency: {consistency:.2%}")

    # Overall assessment
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)

    avg_improvement = sum(r["improvement_percent"] for r in results.values()) / len(results)
    avg_consistency = sum(r["consistency"] for r in results.values()) / len(results)
    avg_f1_with_skill = sum(r["with_skill"]["f1"] for r in results.values()) / len(results)

    print(f"\nAverage Improvement: {avg_improvement:.1f}%")
    print(f"Average Consistency: {avg_consistency:.2%}")
    print(f"Average F1 with Skill: {avg_f1_with_skill:.2f}")

    # Go/No-Go Decision
    print("\n" + "="*80)
    print("GO/NO-GO DECISION")
    print("="*80)

    success_criteria = {
        "Quality Improvement ≥20%": avg_improvement >= 20,
        "Consistency ≥85%": avg_consistency >= 0.85,
        "Follows Instructions": avg_f1_with_skill >= 0.70
    }

    all_passed = all(success_criteria.values())

    for criterion, passed in success_criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {criterion}")

    print("\n" + "="*80)
    if all_passed:
        print("✅ GO: Skills approach is validated. Proceed with Phase 1.")
    else:
        print("❌ NO-GO: Skills approach needs refinement or pivot to structured prompts.")
    print("="*80)

    return results, all_passed

if __name__ == "__main__":
    results, passed = run_phase0_validation()
