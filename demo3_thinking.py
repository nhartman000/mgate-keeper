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
print("DEMO 3: Photosynthesis with Detailed Explanation")
print("="*70)
print(f"\nModel: {model}\n")

question = "What is photosynthesis? Explain the process step by step."
response = keeper.query(question)

print("="*70)
print("DETAILED EXPLANATION")
print("="*70 + "\n")

print(f"{response.content}\n")

print("="*70)
print("QUALITY METRICS")
print("="*70)
print(f"Overall Confidence: {response.overall_confidence * 100:.1f}%")
print(f"Gates Passed: {response.gates_passed}")
print("="*70 + "\n")