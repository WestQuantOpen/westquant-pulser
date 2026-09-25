from westquant_pulser.adapter import PulserAdapter


class Register:
    qubits = {"q0": (0.0, 1.0), "q1": (2.0, 3.0)}


def test_register_import():
    r = PulserAdapter().import_register(Register())
    assert r.payload["n_atoms"] == 2
    assert r.kind.value == "layout"
