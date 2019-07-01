from flask import Flask, render_template
from subprocess import PIPE, run


app = Flask(__name__)


@app.route('/')
def index():
    content = "Hello World!"
    return render_template('control.html', content=content)


@app.route('/fetch')
def fetch():
    command = ['git', 'status']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print(result.returncode, result.stdout, result.stderr)
    return render_template('control.html', content=result.stdout+result.stderr)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
