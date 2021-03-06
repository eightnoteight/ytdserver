#!/usr/bin/python
import subprocess
import time
import pipes
import threading
from flask import Flask, request, render_template, redirect, url_for
app = Flask(__name__)
glock = threading.Lock()
downloads = {}

def ytdl_sh(ytvid):
    if downloads[ytvid]['pause'] or downloads[ytvid]['delete']:
        downloads[ytvid]['running'] = False
        return
    proc = subprocess.Popen(
        "exec youtube-dl --newline {} {}".format(downloads[ytvid]['args'], pipes.quote(ytvid)), 
        shell=True,
        stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if line == '' or downloads[ytvid]['pause'] or downloads[ytvid]['delete']:
            break
        downloads[ytvid]['cmdline'] = line
        # check the 100% downloaded line
        if all(map(line.__contains__, ['[download] ', '%'])): 
            downloads[ytvid]['percentage'] = int(float(line.split()[1][:-1]))
    downloads[ytvid]['pause'] = True
    proc.kill()
    downloads[ytvid]['running'] = False
    return

@app.route('/queue', methods=["POST"])
def queue():
    ytvid = request.form['url']
    if ytvid in downloads:
        return # redirect to dashboard with already in the queue flag set to true
    downloads[ytvid] = {
        'url': ytvid,
        'args': request.form.get('args', ''),
        'percentage': 0,
        'cmdline': '',
        'pause': True,
        'running': False,
        'delete': False
    }
    return redirect(url_for('showdashboard'))
    # return Response(json.dumps(downloads), mimetype='text/json')

@app.route('/getprogress')
def getprogress():
    return render_template(
        "progress.html",
        downloads=downloads)

@app.route('/getverboseprogress')
def getverboseprogress():
    return render_template(
        "verboseprogress.html",
        downloads=downloads)

@app.route('/verbose')
def verbose():
    return render_template("verbose.html", downloads=downloads)

@app.route('/pause', methods=["POST"])
def pause():
    ytvid = request.form['url']
    downloads[ytvid]['pause'] = True
    return redirect(url_for('showdashboard'))
    # return Response(json.dumps(downloads), mimetype='text/json')

@app.route('/resume', methods=["POST"])
def resume():
    ytvid = request.form['url']
    downloads[ytvid]['pause'] = False
    return redirect(url_for('showdashboard'))
    # return Response(json.dumps(downloads), mimetype='text/json')

@app.route('/delete', methods=["POST"])
def delete():
    ytvid = request.form['url']
    downloads[ytvid]['delete'] = True
    return redirect(url_for('showdashboard'))

@app.route('/')
def showdashboard():
    return render_template("ytds.html", downloads=downloads)

def observer():
    while True:
        for ytvid in list(downloads.keys()):
            if not downloads[ytvid]['pause'] and not downloads[ytvid]['running']:
                downloads[ytvid]['running'] = True
                newdownload = threading.Thread(target=ytdl_sh, args=(ytvid,))
                newdownload.daemon = True
                newdownload.start()
            elif all([
                    downloads[ytvid]['pause'],
                    not downloads[ytvid]['running'],
                    downloads[ytvid]['delete']]):
                del downloads[ytvid]
        time.sleep(2)


if __name__ in '__main__':
    worker = threading.Thread(target=observer)
    # KeyboardInterrupt to the main process will abruptly stop the worker daemon
    worker.daemon = True
    worker.start()
    app.run(host='0.0.0.0', port=5000, debug=True)

# for gunicorn
if __name__ == 'app':
    worker = threading.Thread(target=observer)
    # KeyboardInterrupt to the main process will abruptly stop the worker daemon
    worker.daemon = True
    worker.start()
