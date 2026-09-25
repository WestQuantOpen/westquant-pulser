from __future__ import annotations
from typing import Any


def layout_context(layout: Any) -> dict[str, Any]:
    coords = getattr(layout, "coords", None)
    if coords is None:
        traps = getattr(layout, "traps_dict", {})
        coords = list(traps.values())
    return {
        "native_type": type(layout).__name__,
        "slug": getattr(layout, "slug", None),
        "n_traps": len(coords or ()),
        "coordinates": [[float(x) for x in c] for c in (coords or ())],
    }


def deterministic_trap_maps(layout: Any, n_qubits: int) -> dict[str, dict[str, int]]:
    n_traps = len(getattr(layout, "coords", ())) or len(getattr(layout, "traps_dict", {}))
    if n_qubits > n_traps:
        raise ValueError("n_qubits exceeds available traps")
    ids = list(range(n_traps))
    return {
        "identity": {f"q{i}": ids[i] for i in range(n_qubits)},
        "reverse": {f"q{i}": ids[-1-i] for i in range(n_qubits)},
        "even_first": {f"q{i}": (ids[::2] + ids[1::2])[i] for i in range(n_qubits)},
    }
