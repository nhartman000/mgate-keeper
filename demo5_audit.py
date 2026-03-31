#!/usr/bin/env python3
import os
import json
from mgate_keeper import MGateKeeper

if not os.getenv('OPENAI_API_KEY'):
    print("ERROR: Set OPENAI_API_KEY")
    exit(1)

# Load project with gates and context
keeper = MGateKeeper(project_file="mgate_keeper/projects/photosynthesis.mg8")

print("\n" + "="*70)
print("DEMO 5: Complete Audit Trail - Photosynthesis")
print("="*70)
print(f"\nModel: {keeper.llm_model}\n")

question = "What is photosynthesis?"
print(f"Question: {question}\n")

response = keeper.query(user_prompt=question, gates=keeper.gates, context=keeper.context)
answer = response.choices[0].message.content

# Create audit log
audit_log = {
    "audit_id": "AUDIT_PHOTO_DEMO5",
    "query": question,
    "timestamp": "2026-03-31T00:00:00Z",
    "project_id": keeper.project['project_id'],
    "gates_applied": [g.gate_id for g in keeper.gates],
    "context_applied": keeper.context.interpretation_posture,
    "model": keeper.llm_model,
    "response_id": response.id,
    "tokens_used": response.usage.total_tokens,
    "answer": answer
}

print("="*70)
print("AUDIT TRAIL")
print("="*70)
print(f"\nAudit ID: {audit_log['audit_id']}")
print(f"Project ID: {audit_log['project_id']}")
print(f"Gates Applied: {', '.join(audit_log['gates_applied'])}")
print(f"Model: {audit_log['model']}")
print(f"Tokens Used: {audit_log['tokens_used']}")
print(f"\nAnswer:\n{answer}")
print("\n✓ Complete audit trail captured!")
print("="*70 + "\n")

# Save audit log
with open("demo5_audit_log.json", 'w') as f:
    json.dump(audit_log, f, indent=2)
print(f"✓ Audit log saved to demo5_audit_log.json\n")
