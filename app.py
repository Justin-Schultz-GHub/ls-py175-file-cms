import os
from flask import (
                    Flask,
                    render_template,
                    redirect,
                    request,
                    send_from_directory,
                    url_for,
                    )

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('get_files'))

@app.route('/files')
def get_files():
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(root, 'cms', 'data')
    files = [os.path.basename(path) for path in os.listdir(data_dir)]

    return render_template('files.html', files=files)

@app.route('/files/<filename>')
def display_file(filename):
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(root, 'cms', 'data')

    return send_from_directory(data_dir, filename)

if __name__ == "__main__":
    app.run(debug=True, port=8080)