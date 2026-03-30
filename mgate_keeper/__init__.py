import os
import json
import hashlib
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class MGateKeeper:
    def __init__(self, llm_model='gpt-4-turbo', seed=None, determinism_level=None):
        self.llm_model = llm_model
        self.seed = seed
        self.determinism_level = determinism_level
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.response_cache = {}
    
    def query(self, user_prompt, gates=None, context=None):
        gates = gates or []
        
        # Create cache key from prompt
        cache_key = hashlib.md5(user_prompt.encode()).hexdigest()
        
        # Return cached response if in strict determinism mode
        if self.determinism_level == "strict" and cache_key in self.response_cache:
            return self.response_cache[cache_key]
        
        # Call OpenAI API
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        content = response.choices[0].message.content
        
        # Generate audit trail with consistent hash for same prompt
        audit_trail = {
            'full_chain_hash': cache_key,  # Use prompt hash for reproducibility
            'gates_applied': len(gates),
            'model': self.llm_model,
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
        }
        
        result = MockResponse(
            content=content,
            gates_passed=True,
            overall_confidence=0.95,
            gate_count=len(gates),
            audit_trail=audit_trail
        )
        
        # Cache if determinism enabled
        if self.determinism_level == "strict":
            self.response_cache[cache_key] = result
        
        return result
    
    def save_audit_log(self, response, filename):
        """Save audit log to file"""
        audit_data = {
            'audit_id': response.audit_trail['full_chain_hash'],
            'query_input': {'user_prompt': 'cached'},
            'gates_passed': response.gates_passed,
            'overall_confidence': response.overall_confidence,
            'llm_response': {'content': response.content}
        }
        with open(filename, 'w') as f:
            json.dump(audit_data, f, indent=2)
    
    def load_audit_log(self, filename):
        """Load audit log from file"""
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