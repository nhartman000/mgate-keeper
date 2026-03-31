#!/usr/bin/env python3
import os
import json
from mgate_keeper import MGateKeeper

model = os.getenv('MGATE_MODEL', 'gpt-4-turbo')
if not os.getenv('OPENAI_API_KEY'):
    print("ERROR: Set OPENAI_API_KEY")
    exit(1)

keeper = MGateKeeper(llm_model=model)

print("\n" + "="*70)
print("DEMO 5: Complete Audit Trail - Photosynthesis")
print("="*70)
print(f"\nModel: {model}\n")

question = "What is photosynthesis?"
print(f"Question: {question}\n")

response = keeper.query(question)

print("="*70)
print("AUDIT TRAIL")
print("="*70)
print(f"\nResponse ID: {response.audit_trail.get('full_chain_hash', 'N/A')}")
print(f"Gates Applied: {response.audit_trail.get('gates_applied', [])}")
print(f"Model Used: {response.audit_trail.get('model', model)}")
print(f"Prompt Tokens: {response.audit_trail.get('prompt_tokens', 'N/A')}")
print(f"Completion Tokens: {response.audit_trail.get('completion_tokens', 'N/A')}")
print(f"Confidence: {response.overall_confidence * 100:.1f}%")
print(f"\nAnswer:\n{response.content}")
print("\n✓ Complete audit trail captured!")
print("="*70 + "\n")