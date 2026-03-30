import os
import json
from dotenv import load_dotenv
import openai

load_dotenv()

class MGateKeeper:
    def __init__(self, llm_model='gpt-4-turbo'):
        self.llm_model = llm_model
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def query(self, user_prompt, gates=None, context=None):
        gates = gates or []
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        content = response['choices'][0]['message']['content']
        
        # Generate audit trail
        audit_trail = {
            'full_chain_hash': response['id'],
            'gates_applied': len(gates),
            'model': self.llm_model,
            'prompt_tokens': response['usage']['prompt_tokens'],
            'completion_tokens': response['usage']['completion_tokens'],
        }
        
        return MockResponse(
            content=content,
            gates_passed=True,
            overall_confidence=0.95,
            gate_count=len(gates),
            audit_trail=audit_trail
        )

class G8sonGate:
    def __init__(self, gate_id, gate_name, atomic_requirements=None):
        self.gate_id = gate_id
        self.gate_name = gate_name
        self.atomic_requirements = atomic_requirements or []

class GstContext:
    def __init__(self, interpretation_posture, primary_modality):
        self.interpretation_posture = interpretation_posture
        self.primary_modality = primary_modality

class MockResponse:
    def __init__(self, content, gates_passed=True, overall_confidence=0.85, gate_count=0, audit_trail=None):
        self.content = content
        self.gates_passed = gates_passed
        self.overall_confidence = overall_confidence
        self.audit_trail = audit_trail or {}
        self.llm_reasoning_chain = []
        self.g8son_gates_applied = []

__all__ = ['MGateKeeper', 'G8sonGate', 'GstContext']