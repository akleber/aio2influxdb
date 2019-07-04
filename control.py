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
        content += "<a href='get_logfile/{}'>{}</a><br/>\n".format(logfile.name, logfile.name)

    return render_template('control.html', content=content)


@app.route("/get_logfile/<log_name>")
def get_logfile(log_name):
    try:
        return send_from_directory(logs, filename=log_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/delete_logfiles')
def delete_logfiles():
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


@app.route('/pip')
def pip():
    #command = ['python', '_venv/bin/pip', 'install', '-r', 'requirements.txt']
    command = ['env']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    code = result.stdout + result.stderr
    return render_template('control.html', code=code.strip())


@app.route('/restart')
def restart():
    command = ['sudo', 'supervisorctl', 'reread']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    code = result.stdout + result.stderr + "\n"

    command = ['sudo', 'supervisorctl', 'update']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    code = code + result.stdout + result.stderr + "\n"

    command = ['sudo', 'supervisorctl', 'restart', 'all']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    code = code + result.stdout + result.stderr + "\n"

    return render_template('control.html', code=code)


@app.route('/shutdown')
def shutdown():
    command = ['sudo', 'shutdown', '-h', 'now']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return render_template('control.html', code=result.stdout+result.stderr)


@app.route('/reboot')
def reboot():
    command = ['sudo', 'reboot', 'now']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return render_template('control.html', code=result.stdout+result.stderr)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
