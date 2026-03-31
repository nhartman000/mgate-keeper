#!/usr/bin/env python3
import os
import json
from mgate_keeper import MGateKeeper

# Initialize the keeper with the model
model = os.getenv('MGATE_MODEL', 'gpt-4-turbo')
if not os.getenv('OPENAI_API_KEY'):
    print("ERROR: Set OPENAI_API_KEY")
    exit(1)

keeper = MGateKeeper(llm_model=model)

# Ask a question
question = "What is photosynthesis? Explain simply."
response = keeper.query(question)

# Display results
print("\n" + "="*70)
print("DEMO 1: Simple Question")
print("="*70)
print(f"\nModel: {model}\n")
print(f"Answer:\n{response.content}\n")
print(f"Gate Passed: {response.gates_passed}")
print(f"Confidence: {response.overall_confidence * 100:.1f}%")
print(f"\nAudit Trail:")
print(json.dumps(response.audit_trail, indent=2))
print("="*70 + "\n")