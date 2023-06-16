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
database = 'cse6322-quiz2'
driver= '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

@app.route('/')
@app.route('/earthquakes', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        search = request.form['search']
        rangefrom = request.form['rangefrom']
        rangeto = request.form['rangeto']
        idrangefrom = request.form['idrangefrom']
        idrangeto = request.form['idrangeto']
        if len(str(search)) > 0:
            t_qs = cursor.execute('''SELECT * FROM earthquakes e, (SELECT * FROM earthquakes where time=?) as q 
            WHERE e.latitude < (q.latitude + 2) AND e.latitude > (q.latitude - 2)''',(search))
            return render_template('earthquakes.html', earthquakes=t_qs)
        
        elif len(rangefrom) > 0 and len(rangeto) > 0:
            t_qs = cursor.execute("SELECT * from [dbo].[earthquakes] WHERE latitude <='{}' and latitude>='{}' and longitude<='{}' and longitude>='{}'".format(rangeto,rangefrom,idrangeto,idrangefrom))

            # t_qs = cursor.execute('''SELECT * from [dbo].[earthquakes] WHERE latitude <=? and latitude>=? and longitude<=? and longitude>=?)''',(float(rangeto),float(rangefrom),float(idrangeto),float(idrangefrom)))
            return render_template('earthquakes.html', earthquakes=t_qs)

        
        
        
        
        
        t_eqs = []
        for p in earthquakes:
            if p[1] == int(search):
                t_eqs.append(p)
        if len(t_eqs) > 0:
                for t in t_eqs:
                    for k in earthquakes:
                        if k[2] < (t[2] + 2) and (k[2] > t[2] -2):
                            t_eqs.append(k)
                return render_template('earthquakes.html', earthquakes=t_eqs)
        return render_template('earthquakes.html', earthquakes=[], msg="No records found")
              
        # if rangefrom == '':
        #     rangefrom = 0
        # if rangeto == '':
        #     rangeto = 0
        # if idrangefrom == '':
        #     idrangefrom = 0
        # if idrangeto == '':
        #     idrangeto = 0
        # temp_earthquakes = []
        # for p in earthquakes:
            # if p[3] == '':
            #     p[3] = 0
            # if p[2] == '':
            #     p[2] = 0
            # if rangefrom !=0  and rangeto !=0:
            #     if int(p[3]) >= int(rangefrom):
            #         if int(p[3]) <= int(rangeto):
            #             if idrangefrom != 0 and idrangeto != 0:
            #                 if int(p[2]) >= int(idrangefrom):
            #                     if int(p[2]) <= int(idrangeto):
            #                         if search in str(p[5]):
            #                             temp_earthquakes.append(p)
            #                             msg = "grades from {} through {} and ids from {} to {} containing the word {}".format(rangefrom, rangeto, idrangefrom, idrangeto, search)
            #                         # elif len(temp_earthquakes) < 1:
            #                         #     return render_template('earthquakes.html', msg="no information or picture available")
                                    # return render_template('earthquakes.html', earthquakes=temp_earthquakes, msg=msg)
    #                     else:
    #                         temp_earthquakes.append(p)
    #                         msg = "Range in Grades only"
    #     if len(temp_earthquakes) < 1:
    #         return render_template('earthquakes.html', msg="no information or picture available")              
    #     return render_template('earthquakes.html', earthquakes=temp_earthquakes, msg=msg)
    else:
        cursor.execute('SELECT * FROM earthquakes')
        earthquakes = cursor.fetchall()
        return render_template('earthquakes.html', earthquakes=earthquakes)

@app.route('/addrecord', methods=['GET', 'POST'])
def addrecord():
    msg=''
    if request.method == 'POST':
        time = request.form['time']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        mag = request.form['mag']
        net = request.form['net']
        place = request.form['place']
        sql = ('''
        SELECT * FROM earthquakes WHERE time=?
        ''')
        cursor.execute(sql, (time))
        account = cursor.fetchone()
        if account:
            msg = 'Record already exists'
        elif not latitude or not longitude or not mag or not net:
            msg = 'Please fill all details'
        else:
            cursor.execute('''INSERT INTO earthquakes (time,latitude,longitude,mag,net,place) 
                            VALUES (?, ?, ?, ?, ?,?)'''
                         , (time,latitude,longitude,mag,net,place))
            cursor.commit()
            msg = 'You have successfully added !'
            return render_template('addrecord.html', msg=msg)
    # elif request.method == 'POST':
    #     msg = 'Please fill out the form !'
    return render_template('addrecord.html', msg=msg)

# @app.route('/updaterecord/<id>', methods=['GET', 'POST'])
# def updaterecord(id):
#     msg=''
#     cursor.execute('''SELECT * FROM q1c where id=?''', (id))
#     record = cursor.fetchone()
#     return render_template('updaterecord.html', person=record)

# @app.route('/rupdate', methods=['GET', 'POST'])
# def rupdate():
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