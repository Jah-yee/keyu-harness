.PHONY: test ledgers demo audit figures all

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v

ledgers:
	PYTHONPATH=src python3 -m keyu_harness validate-ledger sources references/source_registry.csv
	PYTHONPATH=src python3 -m keyu_harness validate-ledger claims references/claim_ledger.csv
	PYTHONPATH=src python3 -m keyu_harness validate-ledger artifacts references/artifact_registry.csv

demo:
	cd fixtures/replica_2024 && python3 run_demo.py --scenario scenarios/positive.json --out outputs/positive
	cd fixtures/replica_2024 && python3 run_demo.py --scenario scenarios/negative.json --out outputs/negative

audit:
	cd fixtures/replica_2024 && python3 audit_boundary.py

figures:
	@python3 -c "import xml.etree.ElementTree as ET, pathlib; [ET.parse(p) for p in pathlib.Path('assets').glob('*.svg')]; print('all SVGs valid')"

all: test ledgers demo audit figures
