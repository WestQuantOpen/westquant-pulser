from __future__ import annotations

from typing import Any
from westquant_core import Representation, RepresentationKind


class PulserAdapter:
    framework = "pulser"

    def import_register(self, register: Any, *, representation_id: str = "pulser:layout") -> Representation:
        qubits = getattr(register, "qubits", {})
        coords = {
            str(k): [float(x) for x in v]
            for k, v in qubits.items()
        }
        return Representation(
            id=representation_id,
            kind=RepresentationKind.LAYOUT,
            framework=self.framework,
            payload={"n_atoms": len(coords), "coordinates": coords},
            metadata={"native_type": type(register).__name__},
        )
