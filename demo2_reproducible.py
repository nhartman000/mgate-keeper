#!/usr/bin/env python3
import os
from mgate_keeper import MGateKeeper, G8sonGate, GstContext

model = os.getenv('MGATE_MODEL', 'gpt-4-turbo')
if not os.getenv('OPENAI_API_KEY'):
    print("ERROR: Set OPENAI_API_KEY")
    exit(1)

keeper = MGateKeeper(llm_model=model, determinism_level="strict")
gate = G8sonGate(gate_id="G2", gate_name="Test", atomic_requirements=[
    {"req_id": "R1", "requirement": "Answer", "threshold_efficiency": 0.75}
])
context = GstContext(interpretation_posture="Factual", primary_modality="👁️")

print("\n" + "="*70)
print("DEMO 2: Deterministic Response Caching")
print("="*70)
print(f"\nModel: {model}")
print(f"Determinism Level: strict")
print(f"Gates: [G8sonGate(G2)], Context: [GstContext(Factual)]\n")

print("QUERY 1: 'What is photosynthesis? Explain simply.'\n")
response1 = keeper.query(user_prompt="What is photosynthesis? Explain simply.", gates=[gate], context=context)
print(f"Answer 1: {response1.content[:200]}...\n")
print(f"Hash: {response1.audit_trail['full_chain_hash'][:16]}...")
print(f"From Cache: {response1.from_cache}\n")

print("="*70)
print("\nQUERY 2: Same question, same gates, same context\n")
response2 = keeper.query(user_prompt="What is photosynthesis? Explain simply.", gates=[gate], context=context)
print(f"Answer 2: {response2.content[:200]}...\n")
print(f"Hash: {response2.audit_trail['full_chain_hash'][:16]}...")
print(f"From Cache: {response2.from_cache}\n")

print("="*70)
if response1.content == response2.content and response1.audit_trail['full_chain_hash'] == response2.audit_trail['full_chain_hash']:
    print("✅ DETERMINISTIC RESPONSE VERIFIED")
    print(f"✅ Same prompt + gates + context = identical response")
    print(f"✅ Hash: {response1.audit_trail['full_chain_hash'][:16]}... (deterministic)")
    if response2.from_cache:
        print(f"✅ Second call served from cache (no API re-call needed)")
else:
    print("❌ Different")
print("="*70 + "\n")