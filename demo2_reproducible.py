#!/usr/bin/env python3
import os
from mgate_keeper import MGateKeeper, G8sonGate, GstContext

model = os.getenv('MGATE_MODEL', 'gpt-4-turbo')
if not os.getenv('OPENAI_API_KEY'):
    print("ERROR: Set OPENAI_API_KEY")
    exit(1)

keeper = MGateKeeper(llm_model=model, seed=42, determinism_level="strict")
gate = G8sonGate(gate_id="G2", gate_name="Test", atomic_requirements=[
    {"req_id": "R1", "requirement": "Answer", "threshold_efficiency": 0.75}
])
context = GstContext(interpretation_posture="Factual", primary_modality="👁️")

print("\n" + "="*70)
print("DEMO 2: Reproducible (Two API Calls, Same Answer)")
print("="*70)
print(f"\nModel: {model} (seed=42)")
print(f"Gates: [G8sonGate], Context: [GstContext]\n")

print("API CALL 1: 'What is photosynthesis? Explain simply.'\n")
response1 = keeper.query(user_prompt="What is photosynthesis? Explain simply.", gates=[gate], context=context)
print(f"Answer 1:\n{response1.content}\n")
print(f"API Call #{response1.audit_trail['api_call_number']}")
print(f"Seed: {response1.audit_trail['seed']}\n")

print("="*70)
print("\nAPI CALL 2: 'What is photosynthesis? Explain simply.' (same)\n")
response2 = keeper.query(user_prompt="What is photosynthesis? Explain simply.", gates=[gate], context=context)
print(f"Answer 2:\n{response2.content}\n")
print(f"API Call #{response2.audit_trail['api_call_number']}")
print(f"Seed: {response2.audit_trail['seed']}\n")

print("="*70)
if response1.content == response2.content:
    print("✅ IDENTICAL!")
    print(f"✅ TWO REAL API CALLS: Call #{response1.audit_trail['api_call_number']} and Call #{response2.audit_trail['api_call_number']}")
    print(f"✅ DETERMINISTIC: Same seed + gates + context = same answer every time")
else:
    print("❌ Different answers (seed may not be supported on this model)")
print("="*70 + "\n")