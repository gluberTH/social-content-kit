import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_kit import build, catalog, table_csv
from kitlib import count_caption, normalize, safe_path, timestamp, tracked_url
from validate_kit import check_url, validate


class KitTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'examples/campaign.json').read_text(encoding='utf-8'))

    def test_complete_build_and_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'kit'
            build(ROOT / 'examples/campaign.json', root)
            result = validate(root)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['posts'], 8)
            self.assertFalse(result['links_checked'])

    def test_utm_preserves_query_and_fragment(self):
        result = tracked_url('https://example.com/path?a=1&a=2&utm_content=old#details', 'launch', 'x', 'X01')
        self.assertIn('a=1&a=2', result)
        self.assertIn('utm_content=x01', result)
        self.assertTrue(result.endswith('#details'))
        self.assertNotIn('utm_content=old', result)

    def test_previous_utc_day(self):
        local, utc = timestamp('2027-01-04', '00:30', 'Asia/Bangkok')
        self.assertEqual(utc, '2027-01-03T17:30:00+00:00')

    def test_dst_gap_and_overlap(self):
        with self.assertRaisesRegex(ValueError, 'fold'):
            timestamp('2026-10-19', '10:00', 'Asia/Bangkok', 2)
        with self.assertRaises(ValueError):
            timestamp('2026-03-29', '02:30', 'Europe/Berlin')
        with self.assertRaises(ValueError):
            timestamp('2026-10-25', '02:30', 'Europe/Berlin')
        first = timestamp('2026-10-25', '02:30', 'Europe/Berlin', 0)
        second = timestamp('2026-10-25', '02:30', 'Europe/Berlin', 1)
        self.assertNotEqual(first[1], second[1])

    def test_character_budget_includes_final_link(self):
        self.data['posts'][0]['body'] = 'a' * 260
        with self.assertRaisesRegex(ValueError, 'caption'):
            normalize(self.data, ROOT / 'examples')
        self.assertEqual(count_caption('abc https://example.com/long/path', 'x_conservative'), 27)

    def test_custom_platform_and_multilingual_copy(self):
        self.data['platforms'] = {'professional': {'label': 'Professional network', 'caption_limit': 1000, 'alt_limit': 500}}
        self.data['language'] = 'es'
        self.data['posts'] = [self.data['posts'][0]]
        self.data['posts'][0]['platform'] = 'professional'
        self.data['posts'][0]['body'] = 'Una pregunta concreta merece una respuesta útil.'
        self.data['duration_days'] = 10
        normalized = normalize(self.data, ROOT / 'examples')
        normalized['posts'][0]['folder'] = 'professional/example'
        rendered = catalog(normalized)
        self.assertIn('<html lang="en">', rendered)
        self.assertIn('lang="es"', rendered)
        self.assertIn('Professional network', rendered)

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            safe_path(ROOT, '../outside.txt')
        self.data['posts'][0]['image'] = '../LICENSE'
        with self.assertRaises(ValueError):
            normalize(self.data, ROOT / 'examples')

    def test_pin_must_be_portrait_and_separate(self):
        self.data['posts'][1]['image'] = 'images/question-square.png'
        with self.assertRaisesRegex(ValueError, '2:3'):
            normalize(self.data, ROOT / 'examples')

    def test_missing_image_fails_before_output(self):
        self.data['posts'][0]['image'] = 'images/missing.png'
        with self.assertRaisesRegex(ValueError, 'Missing image'):
            normalize(self.data, ROOT / 'examples')

    def test_html_data_is_escaped(self):
        self.data['brand']['name'] = '<script>alert(1)</script>'
        normalized = normalize(self.data, ROOT / 'examples')
        for p in normalized['posts']:
            p['folder'] = 'example/' + p['id']
        rendered = catalog(normalized)
        self.assertNotIn('<script>alert(1)</script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_results_and_unowned_files_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'kit'
            build(ROOT / 'examples/campaign.json', root)
            tracker = root / 'results-tracker.csv'
            tracker.write_text('USER RESULTS\n', encoding='utf-8')
            personal = root / 'notes.txt'
            personal.write_text('keep', encoding='utf-8')
            with self.assertRaises(ValueError):
                build(ROOT / 'examples/campaign.json', root)
            build(ROOT / 'examples/campaign.json', root, overwrite=True)
            self.assertEqual(tracker.read_text(encoding='utf-8'), 'USER RESULTS\n')
            self.assertEqual(personal.read_text(encoding='utf-8'), 'keep')

    def test_metadata_tampering_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'kit'
            build(ROOT / 'examples/campaign.json', root)
            target = root / 'x/2026-10-19_X01/caption.txt'
            target.write_text('changed after approval', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'differs'):
                validate(root)

    def test_duplicate_case_insensitive_ids(self):
        self.data['posts'][1]['id'] = 'x01'
        with self.assertRaisesRegex(ValueError, 'unique'):
            normalize(self.data, ROOT / 'examples')

    def test_private_network_link_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'non-public'):
            check_url('http://127.0.0.1/')

    def test_csv_formula_is_neutralized(self):
        output = table_csv(['caption'], [{'caption': '=1+1'}])
        self.assertIn("'=1+1", output)


if __name__ == '__main__':
    unittest.main()
