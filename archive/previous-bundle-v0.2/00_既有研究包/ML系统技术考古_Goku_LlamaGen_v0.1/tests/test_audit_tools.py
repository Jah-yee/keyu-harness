import json, tempfile, unittest
from pathlib import Path
from src.ml_archaeology.audit_toy_vectors import norm, cosine, sha256
from src.ml_archaeology.audit_sampler_partitions import audit

class AuditTests(unittest.TestCase):
    def test_equal_norm_does_not_mean_equal_content(self):
        a, b = [3.0, 4.0, 0.0], [0.0, 3.0, 4.0]
        self.assertAlmostEqual(norm(a), norm(b))
        self.assertNotEqual(sha256(a), sha256(b))
        self.assertLess(cosine(a, b), 1.0)

    def test_sampler_valid_fixture(self):
        self.assertTrue(audit(8, {"0":[0,2,4,6], "1":[1,3,5,7]})["ok"])

    def test_sampler_invalid_fixture(self):
        result = audit(8, {"0":[0,1,2,3], "1":[2,4,6,7]})
        self.assertFalse(result["ok"])
        self.assertIn(2, result["duplicates"])
        self.assertIn(5, result["missing"])

if __name__ == "__main__":
    unittest.main()
