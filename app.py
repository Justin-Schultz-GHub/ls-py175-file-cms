from markdown import markdown
import os
from flask import (
                    flash,
                    Flask,
                    render_template,
                    redirect,
                    request,
                    send_from_directory,
                    url_for,
                    )

app = Flask(__name__)
app.secret_key='secret1'

# Helper functions
def get_data_dir():
    root = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(root, 'cms', 'data')

def get_file_path(data_dir, filename):
    return os.path.join(data_dir, filename)

def is_valid_path(file_path):
    return os.path.isfile(file_path)

# Route hooks
@app.route('/')
def index():
    return redirect(url_for('get_files'))

@app.route('/files')
def get_files():
    data_dir = get_data_dir()
    files = [os.path.basename(path) for path in os.listdir(data_dir)]

    return render_template('files.html', files=files)

@app.route('/files/<filename>')
def display_file(filename):
    data_dir = get_data_dir()
    file_path = get_file_path(data_dir, filename)

    if is_valid_path(file_path):
        if filename.endswith('.md'):
            with open(file_path, 'r') as file:
                content = file.read()
            return markdown(content)
        else:
            return send_from_directory(data_dir, filename)

    flash(f'"{filename}" does not exist.', 'error')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=8080)