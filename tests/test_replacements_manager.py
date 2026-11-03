import os
import shutil
import tempfile
import unittest

from replacements_manager import ReplacementsManager, build_regex_pattern

class TestReplacementsManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.rep_file = os.path.join(self.test_dir, "replacements.json")
        self.manager = ReplacementsManager(filepath=self.rep_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_and_get_empty(self):
        # File is created lazily when items are saved
        rules = self.manager.get_replacements()
        self.assertEqual(rules, [])
        self.manager.add_replacement("Test", "Prueba")
        self.assertTrue(os.path.exists(self.rep_file))
        self.assertEqual(len(self.manager.get_replacements()), 1)

    def test_add_and_update_rule(self):
        rule = self.manager.add_replacement("Cuvernetes", "Kubernetes", case_sensitive=False, whole_word=True)
        self.assertEqual(rule["find"], "Cuvernetes")
        self.assertEqual(rule["replace"], "Kubernetes")
        self.assertFalse(rule["case_sensitive"])
        self.assertTrue(rule["whole_word"])

        # Add again with updated replacement
        updated = self.manager.add_replacement("cuvernetes", "K8s", case_sensitive=False, whole_word=True)
        self.assertEqual(updated["id"], rule["id"])
        self.assertEqual(updated["replace"], "K8s")

        all_rules = self.manager.get_replacements()
        self.assertEqual(len(all_rules), 1)

    def test_update_by_id(self):
        r1 = self.manager.add_replacement("Dokker", "Docker")
        r2 = self.manager.update_replacement(r1["id"], "Dokker", "Docker CE", case_sensitive=True, whole_word=False)
        self.assertIsNotNone(r2)
        self.assertEqual(r2["replace"], "Docker CE")
        self.assertTrue(r2["case_sensitive"])
        self.assertFalse(r2["whole_word"])

    def test_delete_rule(self):
        r1 = self.manager.add_replacement("Pyton", "Python")
        self.assertEqual(len(self.manager.get_replacements()), 1)
        res = self.manager.delete_replacement(r1["id"])
        self.assertTrue(res)
        self.assertEqual(len(self.manager.get_replacements()), 0)
        # Deleting non-existent
        self.assertFalse(self.manager.delete_replacement("non-existent"))

    def test_build_regex_pattern_whole_word(self):
        reg = build_regex_pattern("API", case_sensitive=False, whole_word=True)
        self.assertTrue(reg.search("usamos la api de pagos"))
        self.assertFalse(reg.search("es una rápida respuesta"))

        # Accented words
        reg_acc = build_regex_pattern("árbol", case_sensitive=False, whole_word=True)
        self.assertTrue(reg_acc.search("plantamos un árbol aquí"))
        self.assertFalse(reg_acc.search("desarbolar la nave"))

    def test_detect_matches_in_segments(self):
        self.manager.add_replacement("cuvernetes", "Kubernetes", case_sensitive=False, whole_word=True)
        self.manager.add_replacement("dokker", "Docker", case_sensitive=False, whole_word=True)
        self.manager.add_replacement("aws", "Amazon Web Services", case_sensitive=True, whole_word=True)

        segments = [
            {"id": 1, "speaker": "Speaker 1", "text": "Hablamos de Cuvernetes y Dokker en la nube."},
            {"id": 2, "speaker": "Speaker 2", "text": "Sí, dokker es genial pero no usamos AWS sino aws."},
            {"id": 3, "speaker": "Speaker 1", "text": "Nada relevante aquí."}
        ]

        matches = self.manager.detect_matches_in_segments(segments)
        self.assertEqual(len(matches), 3)

        match_cuvernetes = next(m for m in matches if m["find"].lower() == "cuvernetes")
        self.assertEqual(match_cuvernetes["count"], 1)
        self.assertEqual(len(match_cuvernetes["segments"]), 1)

        match_dokker = next(m for m in matches if m["find"].lower() == "dokker")
        self.assertEqual(match_dokker["count"], 2)
        self.assertEqual(len(match_dokker["segments"]), 2)

        match_aws = next(m for m in matches if m["find"] == "aws")
        self.assertEqual(match_aws["count"], 1)
        self.assertEqual(match_aws["segments"][0]["segment_id"], 2)

    def test_apply_rules_to_segments(self):
        r1 = self.manager.add_replacement("cuvernetes", "Kubernetes")
        r2 = self.manager.add_replacement("dokker", "Docker")

        segments = [
            {"id": 1, "text": "Instalamos Cuvernetes y dokker."},
            {"id": 2, "text": "Dokker funciona bien con cuvernetes."}
        ]

        updated, total_count, stats = self.manager.apply_rules_to_segments(segments)
        self.assertEqual(total_count, 4)
        self.assertEqual(stats["cuvernetes"], 2)
        self.assertEqual(stats["dokker"], 2)
        self.assertEqual(updated[0]["text"], "Instalamos Kubernetes y Docker.")
        self.assertEqual(updated[1]["text"], "Docker funciona bien con Kubernetes.")

    def test_apply_specific_rule_id(self):
        r1 = self.manager.add_replacement("cuvernetes", "Kubernetes")
        r2 = self.manager.add_replacement("dokker", "Docker")

        segments = [{"id": 1, "text": "Cuvernetes y Dokker"}]
        updated, total_count, stats = self.manager.apply_rules_to_segments(segments, rule_ids=[r1["id"]])
        self.assertEqual(total_count, 1)
        self.assertEqual(updated[0]["text"], "Kubernetes y Dokker")

if __name__ == "__main__":
    unittest.main()
