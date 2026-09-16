import unittest
import xml.etree.ElementTree as ET
from render_profile import build, validate, project_card, ROOT, ICONS
import json
import re


class ProfileTests(unittest.TestCase):
    def test_cursor_follows_title_and_frames_join(self):
        config = json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
        for mobile in [False, True]:
            for title in ['UTool', 'A longer project name that wraps']:
                root = ET.fromstring(project_card(dict(config, project_name=title), mobile))
                ns = {'s': 'http://www.w3.org/2000/svg'}
                labels = root.findall('.//s:text[@font-weight="bold"]', ns)
                cursor = root.find('.//s:rect[@class="cursor"]', ns)
                last = labels[-1]
                expected = float(last.attrib['x']) + float(last.attrib['textLength'])
                self.assertGreaterEqual(float(cursor.attrib['x']), expected)
                self.assertLessEqual(float(cursor.attrib['x'])-expected, 8.01)
                self.assertIsNone(root.find('.//s:path[@id="frame-bottom"]', ns))

    def test_render_and_update(self):
        config = json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
        icons = {name: (ROOT/f'assets/icons/{name}.svg').read_text(encoding='utf-8') for name, _ in ICONS}
        readme = 'Keep me\n<!-- PROFILE:START --><!-- PROFILE:END -->\nKeep me too'
        config.update(project_name='A & <B>', description=('Описание & детали ' * 15).strip(), releases_url='https://example.org/releases?a=1&b=2')
        result = build(config, icons, readme)
        for name, content in result.items():
            if name.endswith('.svg'):
                ET.fromstring(content)
                self.assertNotIn('СЕЙЧАС В РАБОТЕ', content)
        card = next(content for name, content in result.items() if re.fullmatch(r'assets/current-project-[0-9a-f]{12}\.svg', name))
        self.assertIn('A &amp; &lt;B&gt;', card)
        self.assertIn('https://example.org/releases?a=1&amp;b=2', result['README.md'])
        self.assertTrue(result['README.md'].startswith('Keep me\n'))
        self.assertTrue(result['README.md'].endswith('Keep me too'))
        self.assertEqual(build(config, icons, result['README.md']), result)
        for value in ['javascript:alert(1)', 'https://a:b@example.org', 'http://example.org']:
            with self.assertRaises(ValueError):
                validate(dict(config, releases_url=value))


if __name__ == '__main__':
    unittest.main()
