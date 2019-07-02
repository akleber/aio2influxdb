from flask import Flask, render_template, send_from_directory, abort
from subprocess import PIPE, run
from pathlib import Path


app = Flask(__name__)
logs = Path('logs')

@app.route('/')
def index():
    content = "Hello!"
    return render_template('control.html', code=content)


@app.route('/logfiles')
def logfiles():
    content = ""
    logfiles = list(logs.glob('*'))
    for logfile in logfiles:
        content += "<a href='get-logfile/{}'>{}</a><br/>\n".format(logfile.name, logfile.name)

    return render_template('control.html', content=content)


@app.route('/delete-logfiles')
def status():
    command = ['rm', '-f', 'logs/*']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return render_template('control.html', code=result.stdout+result.stderr)


@app.route('/status')
def status():
    command = ['git', 'status']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return render_template('control.html', code=result.stdout+result.stderr)


@app.route('/fetch')
def fetch():
    command = ['git', 'fetch']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return render_template('control.html', code=result.stdout+result.stderr)


@app.route('/rebase')
def rebase():
    command = ['git', 'rebase']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return render_template('control.html', code=result.stdout+result.stderr)


@app.route('/restart')
def restart():
    command = ['ls']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return render_template('control.html', code=result.stdout+result.stderr)


@app.route('/shutdown')
def shutdown():
    command = ['sudo', 'shutdown', '-h', 'now']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return render_template('control.html', code=result.stdout+result.stderr)


@app.route('/reboot')
def shutdown():
    command = ['sudo', 'reboot', 'now']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return render_template('control.html', code=result.stdout+result.stderr)


@app.route("/get-logfile/<log_name>")
def get_logfile(log_name):
    try:
        return send_from_directory(logs, filename=log_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
