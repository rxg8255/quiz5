from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import re
import nltk
from nltk.tokenize import sent_tokenize

app = Flask(__name__)
app.config['UPLOAD_PATH'] = "./uploads"
app.secret_key = 'your secret key'

nltk.download('punkt')
@app.route('/')
@app.route('/earthquakes', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        password = request.form['search']
        l = request.form['count']
        iv = request.form['iv']
        if re.search('[\*/#]', password):
            return render_template('earthquakes.html', msg="Invalid chars */# present")
        if len(password) < 20 and len(password) < int(l):
            return render_template('earthquakes.html', msg="Invalid length lesser than 20 or L")
        password = password[:20]
        if re.search('[A-Z]', password):
            if re.search('[0-9]', password):
                iv_regex = ".*[" + iv + "].*[" + iv + "].*"
                if re.search(iv_regex, password):
                    return render_template('earthquakes.html', msg="Valid")
                else:
                    return render_template('earthquakes.html', msg="No chars present from this - {}".format(iv))
            else:
                return render_template('earthquakes.html', msg="No numbers present")
        else:
            return render_template('earthquakes.html', msg="No uppercase chars present")
    return render_template('earthquakes.html')

@app.route('/text', methods=['GET', 'POST'])
def text():
    if request.method == 'POST':
        notes = request.form['notes']
        m = request.form['m']
        x = request.form['x']
        p = request.form['p']
        l = request.form['l']
        word_len_regex = '[A-Za-z]{' + str(int(l)+1) + '}'
        if re.search(word_len_regex, notes):
            return render_template('textv.html', msg="Word length is more than {}".format(l))
        words_len = len(re.findall(r'\w+', notes))
        if int(m) > words_len:
            return render_template('textv.html', msg="Words less than {}".format(m))
        if words_len > int(x):
            return render_template('textv.html', msg="Words more than {}".format(x))
        sents = sent_tokenize(notes)
        for s in sents:
            if not re.search('^[A-Z].*[?!\.]$', s):
               return render_template('textv.html', msg="Sentences not begins with uppercase or ends with .?! - {}".format(s)) 
        if re.search(',', s):
            parts = s.split(',')
            for pa in parts:
                if len(re.findall(r'\w+',pa)) > int(p):
                  return render_template('textv.html', msg="Part is longer than p - {}".format(pa))   
        return render_template('textv.html', msg="Valid")
    return render_template('textv.html')

@app.route('/banned', methods=['GET', 'POST'])
def banned():
    if request.method == 'POST':
        notes = request.form['notes']
        m = request.form['m']
        b = request.form['b']
        banned_w = b.split(',')
        banned_regex = re.compile('|'.join(map(re.escape, banned_w)))
        words_len = len(re.findall(banned_regex, notes))
        if words_len > int(m):
            return render_template('banned.html', msg="Banned words are more than - {}".format(m))
        else:
            banned_w = b.split(',')
            banned_regex = re.compile('|'.join(map(re.escape, banned_w)))
            cl = banned_regex.sub("", notes)
            return render_template('banned.html', cl=cl)  
    return render_template('banned.html', cl="")