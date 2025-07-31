from markdown import markdown
import os
import string
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
    subdir = 'tests/data' if app.config['TESTING'] else 'cms/data'
    return os.path.join(os.path.dirname(__file__), subdir)

def get_file_path(data_dir, filename):
    return os.path.join(data_dir, filename)

def is_valid_path(file_path):
    return os.path.isfile(file_path)

def is_valid_file_name(name):
    valid_chars = list(string.ascii_letters) + ['-', '_']
    return bool(name) and all(char in valid_chars for char in name)

def file_exists(path):
    return os.path.exists(path)

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

@app.route('/files/<filename>/edit')
def edit_file(filename):
    data_dir = get_data_dir()
    file_path = get_file_path(data_dir, filename)

    with open(file_path, 'r') as file:
        content = file.read()

    return render_template('edit_file.html', file=filename, content=content)

@app.route('/files/<filename>', methods=['POST'])
def save_file(filename):
    data_dir = get_data_dir()
    file_path = get_file_path(data_dir, filename)

    if is_valid_path(file_path):
        new_content = request.form['edit_file']
        with open(file_path, 'w') as file:
            file.write(new_content)

        flash(f'Successfully edited {filename}.', 'success')
        return redirect(url_for('index'))

    flash(f'"{filename}" does not exist.', 'error')
    return redirect(url_for('index'))

@app.route('/files/new')
def new_file():
    return render_template('create_file.html')

@app.route('/files/new/save', methods=['POST'])
def create_file():
    data_dir = get_data_dir()
    filename = request.form['file_name']
    if not filename:
        flash('File name cannot be empty.', 'error')
        return render_template('create_file.html',
                               file_content=request.form['file_content'],
                               file_name=request.form['file_name'],
                               file_extension=request.form['file_extension']
                       ), 422

    elif not is_valid_file_name(filename):
        flash(
                f'File name can only contain letters (A-Z, a-z), '
                f'hyphens (-), and underscores (_).', 'error'
            )
        return render_template('create_file.html',
                               file_content=request.form['file_content'],
                               file_name=request.form['file_name'],
                               file_extension=request.form['file_extension']
                       ), 422

    extension = request.form['file_extension']
    filename += extension

    if file_exists(get_file_path(data_dir, filename)):
        flash('A file with this name already exists.', 'error')
        return render_template('create_file.html',
                               file_content=request.form['file_content'],
                               file_name=request.form['file_name'],
                               file_extension=request.form['file_extension']
                       ), 422

    content = request.form['file_content']

    with open(os.path.join(data_dir, filename), 'w') as file:
        file.write(content)

    flash(f'Successfully created {filename}.', 'success')
    return redirect(url_for('index'))

@app.route('/files/<filename>/delete', methods=['POST'])
def delete_file(filename):
    data_dir = get_data_dir()
    file_path = get_file_path(data_dir, filename)

    if file_exists(file_path):
        os.remove(file_path)

        flash(f'Successfully deleted {filename}.', 'success')
        return redirect(url_for('index'))

    flash(f'The file you are trying to delete does not exist: ({filename})', 'error')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=8080)