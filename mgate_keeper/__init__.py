import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class G8sonGate:
    """A bounded G8SON gate definition used by the MGateKeeper runtime profile."""

    def __init__(
        self,
        gate_id: str,
        gate_name: Optional[str] = None,
        atomic_requirements: Optional[List[Dict[str, Any]]] = None,
        conditions: Optional[List[Any]] = None,
        gate_type: Optional[str] = None,
        outcomes: Optional[Dict[str, Any]] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        self.gate_id = gate_id
        self.gate_name = gate_name or gate_id
        self.atomic_requirements = atomic_requirements or []
        self.conditions = conditions or []
        self.gate_type = gate_type
        self.outcomes = outcomes or {}
        self.raw = raw or {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "G8sonGate":
        return cls(
            gate_id=data.get("gate_id") or data.get("id"),
            gate_name=data.get("gate_name") or data.get("name"),
            atomic_requirements=data.get("atomic_requirements", []),
            conditions=data.get("conditions", []),
            gate_type=data.get("type"),
            outcomes=data.get("outcomes", {}),
            raw=data,
        )

    def control_payload(self) -> Dict[str, Any]:
        requirements = [
            r.get("requirement", r) if isinstance(r, dict) else r
            for r in self.atomic_requirements
        ]
        return {
            "gate_id": self.gate_id,
            "gate_name": self.gate_name,
            "type": self.gate_type,
            "requirements": requirements,
            "conditions": self.conditions,
            "outcomes": self.outcomes,
        }


class GstContext:
    """GST state/context payload used by the MGateKeeper runtime profile."""

    def __init__(
        self,
        context_id: Optional[str] = None,
        interpretation_posture: Optional[str] = None,
        primary_modality: Optional[str] = None,
        constraints: Optional[List[Any]] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        self.context_id = context_id
        self.interpretation_posture = interpretation_posture
        self.primary_modality = primary_modality
        self.constraints = constraints or []
        self.raw = raw or {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GstContext":
        return cls(
            context_id=data.get("context_id") or data.get("state_id"),
            interpretation_posture=data.get("interpretation_posture"),
            primary_modality=data.get("primary_modality"),
            constraints=data.get("constraints", []),
            raw=data,
        )

    def control_payload(self) -> Dict[str, Any]:
        return {
            "context_id": self.context_id,
            "interpretation_posture": self.interpretation_posture,
            "primary_modality": self.primary_modality,
            "constraints": self.constraints,
            "state": self.raw.get("state"),
            "prior": self.raw.get("prior"),
            "current": self.raw.get("current"),
            "internal": self.raw.get("internal"),
            "external": self.raw.get("external"),
            "intent": self.raw.get("intent"),
            "outcome_expectation": self.raw.get("outcome_expectation"),
        }


class MGateKeeper:
    """
    Reproducibility/control experiment runtime for MG8-style gates and GST context.

    This runtime injects the loaded gate requirements and GST context into the model
    request. It does not claim that a provider model is mathematically deterministic;
    reproducibility must be measured empirically for a fixed model/configuration.
    """

    def __init__(
        self,
        llm_model: Optional[str] = None,
        seed: Optional[int] = None,
        determinism_level: Optional[str] = None,
        project_file: Optional[str] = None,
        client: Optional[OpenAI] = None,
    ):
        self.llm_model = llm_model or os.getenv("MGATE_MODEL", "gpt-3.5-turbo")
        self.seed = 42 if seed is None else seed
        self.determinism_level = determinism_level
        self.client = client or OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.project: Optional[Dict[str, Any]] = None
        self.project_path: Optional[Path] = None
        self.project_dir: Optional[Path] = None
        self.gates: List[G8sonGate] = []
        self.context: Optional[GstContext] = None

        if project_file:
            self.load_project(project_file)

    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        # utf-8-sig tolerates historical files that contain a UTF-8 BOM.
        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)

    def _resolve_project_resource(self, resource: str) -> Path:
        path = Path(resource)
        if path.is_absolute():
            return path
        if self.project_dir is None:
            return path
        return self.project_dir / path

    @staticmethod
    def _iter_gate_dicts(data: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        """Support both canonical 1–3 gate files and the earlier single-gate demo shape."""
        gates = data.get("gates")
        if isinstance(gates, list):
            for gate in gates:
                if isinstance(gate, dict):
                    yield gate
            return
        yield data

    def load_project(self, project_file: str) -> None:
        """Load an MG8 project and resolve its resources relative to the project file."""
        self.project_path = Path(project_file).expanduser().resolve()
        self.project_dir = self.project_path.parent
        self.project = self._load_json(self.project_path)

        self.llm_model = os.getenv(
            "MGATE_MODEL", self.project.get("model", self.llm_model)
        )
        self.seed = self.project.get("seed", self.seed)

        self.gates = []
        gate_refs = self.project.get("g8son_gates") or self.project.get("gates") or []
        for gate_ref in gate_refs:
            gate_path = self._resolve_project_resource(gate_ref)
            gate_data = self._load_json(gate_path)
            for gate_dict in self._iter_gate_dicts(gate_data):
                gate = G8sonGate.from_dict(gate_dict)
                if not gate.gate_id:
                    raise ValueError(f"Gate in {gate_path} is missing gate_id")
                self.gates.append(gate)

        context_ref = self.project.get("gst_context")
        if context_ref:
            context_path = self._resolve_project_resource(context_ref)
            self.context = GstContext.from_dict(self._load_json(context_path))
        else:
            self.context = None

    @staticmethod
    def _build_control_message(
        gates: List[G8sonGate], context: Optional[GstContext]
    ) -> str:
        payload = {
            "gst_context": context.control_payload() if context else None,
            "g8son_gates": [gate.control_payload() for gate in gates],
        }
        return (
            "You are executing a bounded MGateKeeper control profile. "
            "Treat the supplied GST constraints and G8SON gate requirements as active "
            "requirements for this response. Do not claim a requirement is satisfied "
            "unless the response actually satisfies it. If the supplied constraints are "
            "insufficient or conflict, state that explicitly rather than silently ignoring "
            "them. Control profile:\n"
            + json.dumps(payload, ensure_ascii=False, sort_keys=True)
        )

    def query(
        self,
        user_prompt: str,
        gates: Optional[List[G8sonGate]] = None,
        context: Optional[GstContext] = None,
    ):
        """Execute a model request with the active G8SON/GST control profile injected."""
        active_gates = self.gates if gates is None else gates
        active_context = self.context if context is None else context
        control_message = self._build_control_message(active_gates, active_context)

        return self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": control_message},
                {"role": "user", "content": user_prompt},
            ],
            seed=self.seed,
            temperature=0,
        )

    def save_audit_log(self, audit_data: Dict[str, Any], filename: str) -> None:
        """Save an audit record. QSON-compliant event construction is profile-specific."""
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)

    def load_audit_log(self, filename: str) -> Dict[str, Any]:
        with Path(filename).open("r", encoding="utf-8-sig") as f:
            return json.load(f)


__all__ = ["MGateKeeper", "G8sonGate", "GstContext"]
