from flask import Flask, render_template, send_from_directory, abort
from subprocess import PIPE, run
from pathlib import Path
from zipfile import ZipFile
import datetime
import shutil


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
        return send_from_directory(str(logs), filename=log_name, as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/get_and_delete')
def get_and_delete():
    zip_path = Path('zip')
    shutil.rmtree(zip_path, ignore_errors=True)
    zip_path.mkdir()

    zip_filename = 'logs-{date:%Y%m%d_%H%M%S}.zip'.format( date=datetime.datetime.now() )

    if logs.is_dir():
        logfiles = list(logs.glob('*'))

    supervisord_log_path = Path('/var/log/supervisor')
    if supervisord_log_path.is_dir():
        supervisor_logfiles = list(supervisord_log_path.glob('*'))

    with ZipFile(zip_path / zip_filename, 'w') as myzip:
        if logfiles:
            for logfile in logfiles:
                myzip.write(logfile)

        if supervisor_logfiles:
            for logfile in supervisor_logfiles:
                myzip.write(logfile)

    command = ['rm -fv logs/*']
    result = run(command, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    code = result.stdout + result.stderr + "\n"

    command = ['rm -fv /var/log/supervisor/*']
    result = run(command, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    code = result.stdout + result.stderr + "\n"
    #return render_template('control.html', code=code)

    return send_from_directory(str(logs), filename=zip_filename, as_attachment=True)


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
    command = ['pip', 'install', '-r', 'requirements.txt']
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
