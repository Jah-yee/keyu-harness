"""Read-only comparison of synthetic vectors. No model files are loaded."""
import argparse, hashlib, json, math
from pathlib import Path

def sha256(values):
    payload = json.dumps(values, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()

def norm(values):
    return math.sqrt(sum(float(x) * float(x) for x in values))

def cosine(a, b):
    na, nb = norm(a), norm(b)
    if na == 0 or nb == 0:
        return None
    return sum(float(x) * float(y) for x, y in zip(a, b)) / (na * nb)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("fixture", type=Path)
    args = ap.parse_args()
    data = json.loads(args.fixture.read_text(encoding="utf-8"))
    a = data["reference"]["values"]
    b = data["comparison"]["values"]
    if len(a) != len(b):
        raise SystemExit("Vector dimensions differ.")
    print("fixture_notice:", data.get("notice", ""))
    print("reference_sha256:", sha256(a))
    print("comparison_sha256:", sha256(b))
    print("reference_l2_norm:", round(norm(a), 8))
    print("comparison_l2_norm:", round(norm(b), 8))
    print("cosine_similarity:", round(cosine(a, b), 8))
    print("max_abs_delta:", round(max(abs(float(x)-float(y)) for x,y in zip(a,b)), 8))
    print("interpretation: equal norms do not establish equal content; this is a synthetic illustration only.")
if __name__ == "__main__":
    main()
