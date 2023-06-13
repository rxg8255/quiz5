from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc
import os
from werkzeug.utils import secure_filename
import blob_access
import re

app = Flask(__name__)
app.config['UPLOAD_PATH'] = "./uploads"
app.secret_key = 'your secret key'

server = 'cse6332-db-server.database.windows.net'
username = 'cse6332-user'
password = 'Test@123'
database = 'quiz1'
driver= '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

@app.route('/')
@app.route('/people', methods=['GET', 'POST'])
def users():
    cursor.execute('SELECT * FROM q1c')
    people = cursor.fetchall()
    if request.method == 'POST':
        search = request.form['search']
        rangefrom = request.form['rangefrom']
        rangeto = request.form['rangeto']
        idrangefrom = request.form['idrangefrom']
        idrangeto = request.form['idrangeto']
        if rangefrom == '':
            rangefrom = 0
        if rangeto == '':
            rangeto = 0
        if idrangefrom == '':
            idrangefrom = 0
        if idrangeto == '':
            idrangeto = 0
        temp_people = []
        for p in people:
            if p[3] == '':
                p[3] = 0
            if p[2] == '':
                p[2] = 0
            if rangefrom and rangeto:
                print(p)
                if int(p[3]) >= int(rangefrom):
                    if int(p[3]) <= int(rangeto):
                        if idrangefrom and idrangeto:
                            if int(p[2]) >= int(idrangefrom):
                                if int(p[2]) <= int(idrangeto):
                                    print(p[5])
                                    print(search)
                                    if search in str(p[5]):
                                        temp_people.append(p)
                                        msg = "grades from {} through {} and ids from {} to {} containing the word {}".format(rangefrom, rangeto, idrangefrom, idrangeto, search)
                                    elif len(temp_people) < 1:
                                        return render_template('people.html', msg="no information or picture available")
                                    return render_template('people.html', people=temp_people, msg=msg)
                        else:
                            temp_people.append(p)
                            msg = "Range in Grades only"
            if len(temp_people) < 1:
                return render_template('people.html', msg="no information or picture available")              
        return render_template('people.html', people=temp_people, msg=msg)
    else:
        return render_template('people.html', people=people)

@app.route('/addrecord', methods=['GET', 'POST'])
def addrecord():
    msg=''
    if request.method == 'POST':
        name = request.form['name']
        s_id = request.form['s_id']
        grade = request.form['grade']
        image = request.files['image']
        notes = request.form['notes']
        filename = filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        upload_status = blob_access.upload_blob(filename)
        print(upload_status)
        if upload_status[0] == 'Success':
            temp_filename = upload_status[1]
            picture_url = 'https://cse6332sa.blob.core.windows.net/images/' + temp_filename
        else:
            msg = 'Failed to upload file!!'
            return render_template('addrecord.html', msg=msg)
        sql = ('''
        SELECT * FROM q1c WHERE s_id=?
        ''')
        cursor.execute(sql, (s_id))
        account = cursor.fetchone()
        if account:
            msg = 'Record already exists'
        elif not name or not s_id or not grade or not notes:
            msg = 'Please fill all details'
        else:
            cursor.execute('''INSERT INTO q1c (name,s_id,grade,picture_url,notes) 
                            VALUES (?, ?, ?, ?, ?)'''
                         , (name, s_id, grade, picture_url, notes))
            cursor.commit()
            msg = 'You have successfully added !'
            return render_template('addrecord.html', msg=msg)
    # elif request.method == 'POST':
    #     msg = 'Please fill out the form !'
    return render_template('addrecord.html', msg=msg)

@app.route('/updaterecord/<id>', methods=['GET', 'POST'])
def updaterecord(id):
    msg=''
    cursor.execute('''SELECT * FROM q1c where id=?''', (id))
    record = cursor.fetchone()
    return render_template('updaterecord.html', person=record)

@app.route('/rupdate', methods=['GET', 'POST'])
def rupdate():
    msg='Failed to update'
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        s_id = request.form['s_id']
        grade = request.form['grade']
        notes = request.form['notes']
        if request.files['image']:
            print('IN')
            image = request.files['image']
            filename = filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            upload_status = blob_access.upload_blob(filename)
            print(upload_status)
            if upload_status[0] == 'Success':
                temp_filename = upload_status[1]
                picture_url = 'https://cse6332sa.blob.core.windows.net/images/' + temp_filename
                cursor.execute('''UPDATE q1c SET picture_url=? WHERE id=?''',(picture_url, id))

        cursor.execute("UPDATE q1c SET name='{}', s_id='{}', notes='{}', grade='{}' "
                     "where id={}".format(name, s_id, notes, grade, id))
        cursor.commit()
        msg = 'Record successfully updated !'
        return redirect('/')
    return render_template('updaterecord.html', msg=msg)

@app.route('/deleterecord/<id>', methods=['GET', 'POST'])
def deleterecord(id):
    msg=''
    cursor.execute("DELETE FROM q1c where id={}".format(id))
    cursor.commit()
    msg = 'Record successfully deleted !'
    return redirect('/')