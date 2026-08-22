#!/usr/bin/env python3
import os
from pathlib import Path

from mgate_keeper import MGateKeeper

if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: Set OPENAI_API_KEY")
    raise SystemExit(1)

keeper = MGateKeeper(project_file="mgate_keeper/projects/photosynthesis.mg8")

print("\n" + "=" * 70)
print("DEMO 2: Reproducibility Experiment with G8SON + GST Controls")
print("=" * 70)

print("\nProject:", keeper.project["project_name"])
print("Project ID:", keeper.project["project_id"])

print(f"\nG8SON gates loaded ({len(keeper.gates)}):")
for gate in keeper.gates:
    print(f"  - {gate.gate_id}: {gate.gate_name}")
    for req in gate.atomic_requirements:
        print(f"      * {req.get('requirement', req)}")

print("\nGST context:")
print("  posture:", keeper.context.interpretation_posture)
print("  modality:", keeper.context.primary_modality)
print("  constraints:")
for constraint in keeper.context.constraints:
    print("    *", constraint)

prompt = "What is photosynthesis? Explain simply."
print("\nPrompt:", repr(prompt))

print("\n" + "=" * 70)
print("API CALL #1")
print("=" * 70)
response1 = keeper.query(prompt)
answer1 = response1.choices[0].message.content
print(answer1)

print("\n" + "=" * 70)
print("API CALL #2 — same project, prompt, seed, temperature, gates, and GST context")
print("=" * 70)
keeper2 = MGateKeeper(project_file="mgate_keeper/projects/photosynthesis.mg8")
response2 = keeper2.query(prompt)
answer2 = response2.choices[0].message.content
print(answer2)

identical = answer1 == answer2

audit_log = {
    "qson_version": "1.0",
    "run_id": keeper.project.get("run_trace_id", "RUN_DEMO_PHOTO"),
    "experiment": "fixed-control reproducibility",
    "query": prompt,
    "project_id": keeper.project["project_id"],
    "gate_ids": [g.gate_id for g in keeper.gates],
    "gst_context_id": keeper.context.context_id,
    "model": keeper.llm_model,
    "seed": keeper.seed,
    "temperature": 0,
    "identical_outputs_observed": identical,
    "responses": [
        {"call_number": 1, "response_id": response1.id, "content": answer1},
        {"call_number": 2, "response_id": response2.id, "content": answer2},
    ],
    "note": (
        "An identical pair is an empirical observation for this run, not a universal "
        "guarantee of provider-level determinism."
    ),
}

output_ref = keeper.project["qson_audit_log"]
output_path = Path(keeper.project_path).parent / output_ref
keeper.save_audit_log(audit_log, str(output_path))

print("\n" + "=" * 70)
if identical:
    print("MATCH OBSERVED: the two returned texts are identical")
else:
    print("VARIATION OBSERVED: the two returned texts differ")
print("Audit record:", output_path)
print("=" * 70 + "\n")
