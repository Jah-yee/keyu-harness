"""Audit synthetic distributed sample partitions for coverage and overlap."""
import argparse, json
from pathlib import Path

def audit(dataset_size, ranks):
    all_items = []
    for rank, items in ranks.items():
        for item in items:
            if not isinstance(item, int) or item < 0 or item >= dataset_size:
                return {"ok": False, "reason": "out_of_range", "rank": rank, "item": item}
            all_items.append(item)
    duplicates = sorted({x for x in all_items if all_items.count(x) > 1})
    missing = sorted(set(range(dataset_size)) - set(all_items))
    return {
        "ok": not duplicates and not missing and len(all_items) == dataset_size,
        "dataset_size": dataset_size,
        "observed_count": len(all_items),
        "duplicates": duplicates,
        "missing": missing,
        "note": "Toy fixture audit only; not an implementation of or patch to PyTorch DistributedSampler."
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("fixture", type=Path)
    args = ap.parse_args()
    data = json.loads(args.fixture.read_text(encoding="utf-8"))
    print(data.get("notice", ""))
    for case in data["cases"]:
        result = audit(data["dataset_size"], case["ranks"])
        print(json.dumps({"case": case["name"], **result}, ensure_ascii=False))
if __name__ == "__main__":
    main()
