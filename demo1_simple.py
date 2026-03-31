#!/usr/bin/env python3
import os
import json
from mgate_keeper import MGateKeeper

if not os.getenv('OPENAI_API_KEY'):
    print("ERROR: Set OPENAI_API_KEY")
    exit(1)

# Initialize the keeper
keeper = MGateKeeper(llm_model="gpt-3.5-turbo")

# Ask a question
question = "What is photosynthesis? Explain simply."
response = keeper.query(question)

# Display results
print("\n" + "="*70)
print("DEMO 1: Simple Question")
print("="*70)
print(f"\nModel: gpt-3.5-turbo\n")
print(f"Answer:\n{response.choices[0].message.content}\n")
print(f"Confidence: {response.usage.completion_tokens}")
print(f"\nResponse ID: {response.id}")
print("="*70 + "\n")
