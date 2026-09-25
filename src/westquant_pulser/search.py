from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Callable, Sequence

from westquant_core import Action, DeterministicBeamSearch, Evaluation, Objective


STAGES = ("mapping", "duration", "amplitude", "detuning")


@dataclass(frozen=True)
class PulserSearchSpace:
    mapping: tuple[str, ...] = ("identity",)
    duration: tuple[float, ...] = (0.75, 1.0, 1.25)
    amplitude: tuple[float, ...] = (0.75, 1.0, 1.25)
    detuning: tuple[float, ...] = (0.5, 1.0, 1.5)

    def choices(self, stage: str) -> tuple[Any, ...]:
        return tuple(getattr(self, stage))


@dataclass(frozen=True)
class ConstantPulseTemplate:
    register: Any
    device: Any
    channel_id: str = "rydberg_global"
    channel_name: str = "rydberg_global"
    duration_ns: int = 1000
    amplitude: float = 3.14
    detuning: float = 0.0
    phase: float = 0.0
    measure: bool = False

    def build(self, config: dict[str, Any]) -> Any:
        import pulser
        mapping = str(config.get("mapping", "identity"))
        if mapping != "identity":
            raise ValueError("ConstantPulseTemplate only supports identity mapping; supply a custom builder for trap search")
        duration = max(1, int(round(self.duration_ns * float(config.get("duration", 1.0)))))
        amplitude = self.amplitude * float(config.get("amplitude", 1.0))
        detuning = self.detuning * float(config.get("detuning", 1.0))
        seq = pulser.Sequence(self.register, self.device)
        seq.declare_channel(self.channel_name, self.channel_id)
        pulse = pulser.Pulse.ConstantPulse(duration, amplitude, detuning, self.phase)
        seq.add(pulse, self.channel_name)
        if self.measure:
            seq.measure()
        return seq


def prefix_config(prefix: Sequence[Action]) -> dict[str, Any]:
    return {a.stage: a.parameters.get("value", a.name) for a in prefix}


def sequence_metrics(sequence: Any) -> dict[str, Any]:
    duration = None
    try:
        duration = int(sequence.get_duration())
    except Exception:
        pass
    n_atoms = None
    min_distance = None
    try:
        reg = sequence.get_register()
        qubits = getattr(reg, "qubits", {})
        coords = list(qubits.values())
        n_atoms = len(coords)
        if len(coords) >= 2:
            dists = []
            for i in range(len(coords)):
                for j in range(i + 1, len(coords)):
                    a, b = coords[i], coords[j]
                    dists.append(math.sqrt(sum((float(x)-float(y))**2 for x,y in zip(a,b))))
            min_distance = min(dists) if dists else None
    except Exception:
        pass
    return {
        "duration_ns": duration,
        "n_atoms": n_atoms,
        "min_atom_distance": min_distance,
        "n_declared_channels": len(getattr(sequence, "declared_channels", {})),
    }


class PulserVerifier:
    def verify(self, sequence: Any) -> dict[str, Any]:
        try:
            abstract = sequence.to_abstract_repr()
            return {"equivalence": "same_problem_different_dynamics", "verified": True, "method": "Pulser Sequence validation+serialization", "abstract_repr_bytes": len(abstract)}
        except Exception as exc:
            return {"equivalence": "unknown", "verified": False, "reason": type(exc).__name__, "message": str(exc)}


class PulserSequentialSearch:
    def __init__(self, *, builder: Callable[[dict[str, Any]], Any], search_space: PulserSearchSpace | None = None,
                 beam_width: int = 3, evaluator: Callable[[Any], dict[str, Any]] | None = None,
                 verifier: Any | None = None) -> None:
        self.builder = builder
        self.search_space = search_space or PulserSearchSpace()
        self.evaluator = evaluator or sequence_metrics
        self.verifier = verifier or PulserVerifier()
        self.engine = DeterministicBeamSearch(
            stages=STAGES,
            beam_width=beam_width,
            objectives=(Objective("duration_ns"),),
        )

    def run(self, *, challenge_id: str = "pulser-challenge"):
        def actions(stage, prefix):
            out=[]
            for value in self.search_space.choices(stage):
                name = str(value)
                out.append(Action(stage, name, {"value": value}))
            return out

        def evaluate(prefix):
            start=time.perf_counter()
            try:
                seq=self.builder(prefix_config(prefix))
                metrics=self.evaluator(seq)
                return Evaluation(success=True, metrics=metrics, verification=self.verifier.verify(seq), cost={"build_seconds":time.perf_counter()-start})
            except Exception as exc:
                return Evaluation(success=False, error={"type":type(exc).__name__,"message":str(exc)}, cost={"build_seconds":time.perf_counter()-start})
        return self.engine.run(challenge_id=challenge_id, actions=actions, evaluate=evaluate)
