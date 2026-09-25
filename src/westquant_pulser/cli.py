from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path
from westquant_core import write_jsonl
from .search import PulserSequentialSearch


def main() -> None:
    p=argparse.ArgumentParser(description="WestQuant sequential control search for Pulser")
    p.add_argument("--module", required=True, help="Python module containing build_sequence(config)")
    p.add_argument("--beam-width", type=int, default=3)
    p.add_argument("--output", default="results/westquant-pulser")
    args=p.parse_args()
    spec=importlib.util.spec_from_file_location("wq_pulser_problem", args.module)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load module")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    result=PulserSequentialSearch(builder=mod.build_sequence, beam_width=args.beam_width).run(challenge_id=Path(args.module).stem)
    out=Path(args.output); out.mkdir(parents=True, exist_ok=True)
    (out/"summary.json").write_text(json.dumps({"best":result.best.to_dict() if result.best else None,"n_states":len(result.states)},indent=2),encoding="utf-8")
    write_jsonl(out/"trajectory.jsonl", result.records(framework="pulser"))
if __name__=="__main__": main()
