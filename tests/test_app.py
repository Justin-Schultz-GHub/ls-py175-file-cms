import unittest
from app import app

class AppTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/files', response.headers['Location'])

    def test_get_files(self):
        response = self.client.get('/files')
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('<h2>File List:</h2>', data)
        self.assertIn('about.txt', data)
        self.assertIn('changes.txt', data)
        self.assertIn('history.txt', data)

    def test_display_file(self):
        test_cases = {
            'about.txt': 'This is my app.',
            'changes.txt': 'There are many changes.',
            'history.txt': '1989 - Guido van Rossum starts developing Python.'
        }

        for file_name, expected_string in test_cases.items():
            with self.client.get(f'/files/{file_name}') as response:
                self.assertEqual(response.status_code, 200, msg=f"Failed on {file_name}")
                response_text = response.get_data(as_text=True)
                self.assertIn(expected_string, response_text, msg=f'Failed on file: {file_name}')
