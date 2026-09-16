import unittest
import xml.etree.ElementTree as ET
from render_profile import build, validate, ROOT, ICONS
import json


class ProfileTests(unittest.TestCase):
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
        self.assertIn('A &amp; &lt;B&gt;', result['assets/current-project.svg'])
        self.assertIn('https://example.org/releases?a=1&amp;b=2', result['README.md'])
        self.assertTrue(result['README.md'].startswith('Keep me\n'))
        self.assertTrue(result['README.md'].endswith('Keep me too'))
        self.assertEqual(build(config, icons, result['README.md']), result)
        for value in ['javascript:alert(1)', 'https://a:b@example.org', 'http://example.org']:
            with self.assertRaises(ValueError):
                validate(dict(config, releases_url=value))


if __name__ == '__main__':
    unittest.main()
