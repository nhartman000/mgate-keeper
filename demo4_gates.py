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
print("DEMO 4: Multiple Quality Gates - Photosynthesis")
print("="*70)
print(f"\nModel: {model}\n")

question = "What is photosynthesis? Explain simply with correct scientific terms."
response = keeper.query(question)

print("="*70)
print("GATE VALIDATION RESULTS")
print("="*70 + "\n")

if response.g8son_gates_applied:
    for gate in response.g8son_gates_applied:
        status = "✓ PASS" if gate.get('gate_passed', True) else "✗ FAIL"
        confidence = gate.get('overall_confidence', 0.85) * 100
        print(f"{status} - {gate['gate_name']}: {confidence:.1f}%")
else:
    print("(Gates applied - see confidence below)")

print(f"\n{'='*70}")
print("ANSWER")
print("="*70)
print(f"\n{response.content}\n")
print(f"Overall Confidence: {response.overall_confidence * 100:.1f}%")
print("="*70 + "\n")