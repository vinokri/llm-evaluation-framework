import random

def llm_judge(task, model_name, candidate_output):
    det = task["deterministic"][model_name]
    ratio = det["passed"] / det["total"]

    # Synthetic judge rubric used by the local portfolio demo.
    if model_name == "Model A":
        correctness, reasoning, minimality, instruction = 4.9, 4.8, 4.9, 4.9
        rationale = "Directly addresses the task, preserves expected behavior, and makes focused changes with strong validation."
    elif model_name == "Model C":
        correctness, reasoning, minimality, instruction = 4.2, 4.1, 3.3, 3.8
        rationale = "Mostly correct, but introduces unnecessary changes or misses part of the requested validation."
    else:
        correctness, reasoning, minimality, instruction = 2.4, 2.3, 2.7, 2.2
        rationale = "Partially relevant, but misses important task requirements and does not provide sufficient verification."

    # Nudge overall with deterministic test signal.
    overall = round((correctness + reasoning + minimality + instruction) / 4 * 0.7 + (ratio * 5) * 0.3, 2)

    return {
        "overall_score": overall,
        "correctness": correctness,
        "reasoning_quality": reasoning,
        "minimality_safety": minimality,
        "instruction_following": instruction,
        "rationale": rationale,
        "deterministic_passed": det["passed"],
        "deterministic_total": det["total"],
        "latency_ms": round(random.uniform(650, 1450), 0),
        "mode": "simulated LLM judge"
    }
