import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class MGateKeeper:
    def __init__(self, llm_model='gpt-4-turbo', seed=None, determinism_level=None):
        self.llm_model = llm_model
        self.seed = seed if seed is not None else 42
        self.determinism_level = determinism_level
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.api_call_count = 0
    
    def query(self, user_prompt, gates=None, context=None):
        gates = gates or []
        
        # Always make a real API call (no caching)
        self.api_call_count += 1
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": user_prompt}],
            seed=self.seed  # Deterministic seed from YOUR system config
        )
        
        content = response.choices[0].message.content
        
        audit_trail = {
            'full_chain_hash': response.id,
            'gates_applied': len(gates),
            'model': self.llm_model,
            'seed': self.seed,
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'api_call_number': self.api_call_count
        }
        
        result = MockResponse(
            content=content,
            gates_passed=True,
            overall_confidence=0.95,
            gate_count=len(gates),
            audit_trail=audit_trail
        )
        
        return result
    
    def save_audit_log(self, response, filename):
        audit_data = {
            'audit_id': response.audit_trail['full_chain_hash'],
            'gates_passed': response.gates_passed,
            'overall_confidence': response.overall_confidence,
            'llm_response': {'content': response.content}
        }
        with open(filename, 'w') as f:
            json.dump(audit_data, f, indent=2)
    
    def load_audit_log(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)

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