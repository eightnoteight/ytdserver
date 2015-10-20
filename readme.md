# ytdserver
a web ui for scheduling your youtube-dl downloads interactively.

### requirements
flask, youtube-dl, gunicorn

## running
    mkdir ytdserver
    cd ytdserver
    virtualenv --python=python2.7 .venv  # create a virtualenv
    source ./.venv/bin/activate
    pip install flask youtube-dl
    git clone https://github.com/eightnoteight/ytdserver.git
    cd ytdserver/ytdserver
    gunicorn --enable-stdio-inheritance -w 1 -b 0.0.0.0:5000 app:app --error-logfile - --access-logfile -
    # if you haven't installed gunicorn, you can simply run the app.py as normal python script
    python app.py

ps: it is important that you run gunicorn with one worker because the data sync hasn't been implemented yet.


### Screenshots
![](http://i.imgur.com/VKHZLmd.png) 
![](http://i.imgur.com/mKoQrQt.png) 
![](http://i.imgur.com/PBmLt5U.png)

### todo:
- [ ] Sticky Navbar
- [ ] convert downloads dictionary into a monitor interfaced dictionary. (thread safe)  ***
- [ ] use a sql database to save the state of the server, i.e global downloads dictionary.
- [ ] download the file option in the webui.
- [ ] instead of parsing the youtube-dl command output use youtube_dl api
- [ ] try to make a docker image and test it either using interface bridges or mitmproxy.

