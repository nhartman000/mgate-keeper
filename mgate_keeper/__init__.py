import os
from dotenv import load_dotenv

load_dotenv()

class MGateKeeper:
    def __init__(self, llm_model='gpt-4-turbo'):
        self.llm_model = llm_model
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.google_key = os.getenv('GOOGLE_API_KEY')
    
    def query(self, user_prompt, gates=None, context=None):
        gates = gates or []
        return MockResponse(
            content=f"Response to: {user_prompt}\n\nUsing model: {self.llm_model}",
            gates_passed=True,
            overall_confidence=0.85,
            gate_count=len(gates)
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
    def __init__(self, content, gates_passed=True, overall_confidence=0.85, gate_count=0):
        self.content = content
        self.gates_passed = gates_passed
        self.overall_confidence = overall_confidence
        self.audit_trail = {'full_chain_hash': 'abc123def456'}

__all__ = ['MGateKeeper', 'G8sonGate', 'GstContext']