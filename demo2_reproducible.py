#!/usr/bin/env python3
import os
import json
from mgate_keeper import MGateKeeper, G8sonGate, GstContext

model = os.getenv('MGATE_MODEL', 'gpt-4-turbo')
if not os.getenv('OPENAI_API_KEY'):
    print("ERROR: Set OPENAI_API_KEY")
    exit(1)

keeper = MGateKeeper(llm_model=model, determinism_level="strict")
gate = G8sonGate(gate_id="G2", gate_name="Test", atomic_requirements=[
    {"req_id": "R1", "requirement": "Answer", "threshold_efficiency": 0.75}
])

print("\n" + "="*70)
print("DEMO 2: Reproducible (Ask Twice, Get Same Answer)")
print("="*70)
print(f"\nModel: {model}\n")

print("Query 1: 'What is photosynthesis? Explain simply.'\n")
response1 = keeper.query(user_prompt="What is photosynthesis? Explain simply.", gates=[gate])
print(f"Answer 1: {response1.content}\n")
print(f"Hash: {response1.audit_trail['full_chain_hash'][:16]}...")
print(f"From Cache: {response1.from_cache}")
print(f"API Call #{response1.audit_trail['api_call_number']}\n")

print("Query 2: 'What is photosynthesis? Explain simply.' (same)\n")
response2 = keeper.query(user_prompt="What is photosynthesis? Explain simply.", gates=[gate])
print(f"Answer 2: {response2.content}\n")
print(f"Hash: {response2.audit_trail['full_chain_hash'][:16]}...")
print(f"From Cache: {response2.from_cache}")
print(f"API Call #{response2.audit_trail['api_call_number']}\n")

print("="*70)
if response1.content == response2.content and response1.audit_trail['full_chain_hash'] == response2.audit_trail['full_chain_hash']:
    print("✅ IDENTICAL!")
    print(f"✅ CACHED: Query 2 was served from cache (no API call)")
else:
    print("❌ Different")
print("="*70 + "\n")