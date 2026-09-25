# westquant-pulser

Neutral-atom representation/control search extracted from the ideas proven in
WestQuant Open Artifact #001 (QoolQit Representation Stack).

The alpha search exposes four explicit decisions:

```text
mapping -> duration scale -> amplitude scale -> detuning scale
```

`ConstantPulseTemplate` gives a minimal runnable Sequence builder. Real research
should inject a device-specific builder that knows calibrated `RegisterLayout`,
mappable-register, channel and waveform constraints.

Pulser validation/serialization failures are retained as negative policy data.
The default verification label is `same_problem_different_dynamics`, not
`exact`, because changing control schedules is not generally unitary-equivalent
in the strong compiler sense.

## Native smoke

```bash
pip install -e ../westquant-core -e .[test]
pytest -q
python integration/smoke.py
```
