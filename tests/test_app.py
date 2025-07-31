import html
import os
import shutil
import unittest
from app import app, get_data_dir, get_file_path

class AppTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.data_path = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_path, exist_ok=True)

        test_cases = {
            'about.md': '# About This Project',
            'changes.txt': 'There are many changes.',
            'history.txt': '1989 - Guido van Rossum starts developing Python.'
        }

        for key, value in test_cases.items():
            self.create_document(key, value)

    def create_document(self, name, content=""):
        with open(os.path.join(self.data_path, name), 'w') as file:
            file.write(content)

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

    def test_get_files(self):
        response = self.client.get('/files')
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        self.assertIn('about.md', data)
        self.assertIn('changes.txt', data)
        self.assertIn('history.txt', data)

    def test_display_file(self):
        test_cases = {
            'about.md': 'About This Project',
            'changes.txt': 'There are many changes.',
            'history.txt': '1989 - Guido van Rossum starts developing Python.'
        }

        for file_name, expected_string in test_cases.items():
            with self.client.get(f'/files/{file_name}') as response:
                self.assertEqual(response.status_code, 200, msg=f"Failed on {file_name}")
                response_text = response.get_data(as_text=True)
                self.assertIn(expected_string, response_text, msg=f'Failed on file: {file_name}')

    def test_file_not_found(self):
        fake_file = 'fake.txt'
        with self.client.get(f'/files/{fake_file}', follow_redirects=True) as response:
            self.assertEqual(response.status_code, 200)
            unescaped_response_text = html.unescape(response.get_data(as_text=True))
            self.assertIn(f'"{fake_file}" does not exist.', unescaped_response_text)

        with self.client.get(f'/') as response:
            unescaped_response_text = html.unescape(response.get_data(as_text=True))
            self.assertNotIn(f'"{fake_file}" does not exist.',
                            unescaped_response_text)

    def test_markdown_display(self):
        with self.client.get(f'/files/about.md') as response:
            self.assertEqual(response.status_code, 200)
            response_text = response.get_data(as_text=True)
            self.assertIn(f'<h1>About This Project</h1>', response_text)

    def test_edit_file_page(self):
        response = self.client.get('/files/changes.txt/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn("<textarea", response.get_data(as_text=True))
        self.assertIn('<input type="submit" value="Save"/>', response.get_data(as_text=True))

    def test_save_file(self):
        test_files = ['changes.txt','about.md', 'history.txt']
        data_dir = get_data_dir()

        for filename in test_files:
            file_path = get_file_path(data_dir, filename)
            with open(file_path, 'r') as file:
                original_content = file.read()

            new_content = 'This is a test.'
            response = self.client.post(
                        f'/files/{filename}',
                        data={'edit_file': new_content},
                        content_type='application/x-www-form-urlencoded'
                    )
            self.assertEqual(response.status_code, 302)
            with open(file_path, 'r') as file:
                self.assertEqual(new_content, file.read())

            with open(file_path, 'w') as file:
                file.write(original_content)

    def test_display_new_file_page(self):
        response = self.client.get('/files/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<h1>Create a New File', response.get_data(as_text=True))
        self.assertIn('<textarea name="file_content">', response.get_data(as_text=True))

    def test_create_file(self):
        response = self.client.post('/files/new/save',
                                    data={
                                        'file_name': 'Test_File',
                                        'file_extension': '.md',
                                        'file_content': 'This is a test',
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Successfully created Test_File.md',
                        response.get_data(as_text=True)
                        )
        response = self.client.get('/files')
        self.assertIn('Test_File.md', response.get_data(as_text=True))

    def test_create_nameless_file(self):
        response = self.client.post('/files/new/save',
                                    data={
                                        'file_name': '',
                                        'file_extension': '.md',
                                        'file_content': 'This is a test',
                                    })
        self.assertEqual(response.status_code, 422)
        self.assertIn('File name cannot be empty.', response.get_data(as_text=True))
        self.assertIn('This is a test', response.get_data(as_text=True))
        self.assertIn('<option value=".md" selected>', response.get_data(as_text=True))

    def tearDown(self):
        shutil.rmtree(self.data_path, ignore_errors=True)