import os
from flask import Flask, render_template, request, redirect, url_for
from time import sleep
from icalendar import Calendar

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        name1 = request.form['name1'].lower()
        name2 = request.form['name2'].lower()
        
        try:
            g = open(UPLOAD_FOLDER + name1 + '.ics')
        except FileNotFoundError:
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>User not found</title>
            </head>
            <body bgcolor="#181a1b" text="#e8e6e3">
            {name1}\'s schedule not found. <br>Upload it using the button below to add it to database, or use incognito mode. 
            <form action="/upload"><input type="submit" value="Upload file"></form><form action="/">
            <input type="submit" value="Go back."></form>
            </body>
            </html>'''

        try:
            g1 = open(UPLOAD_FOLDER + name2 + '.ics')
        except FileNotFoundError:
            return f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>User not found</title>
            </head>
            <body bgcolor="#181a1b" text="#e8e6e3">
            {name2}\'s schedule not found. <br>Upload it using the button below to add it to database, or use incognito mode. 
            <form action="/upload"><input type="submit" value="Upload file"></form><form action="/">
            <input type="submit" value="Go back."></form>
            </body>
            </html>'''

        gcal = Calendar.from_ical(g.read())
        gcal1 = Calendar.from_ical(g1.read())

        common = 0
        common_list = []

        for component in gcal.walk():
            for component1 in gcal1.walk():
                if component.name == "VEVENT" and component1.name == "VEVENT":
                    if (component1.get("summary") == component.get('summary')):
                        common += 1
                        common_list.append(component.get('summary').strip('*').split('(')[0])
        g.close()
        g1.close()

        result_string = ""
        if(common > 0):
            result_string = f'''<!DOCTYPE html>
                                <html>
                                <head>
                                    <title>ICal Result :D</title>
                                </head>
                                <body bgcolor="#181a1b" text="#e8e6e3">
                                You guys have {common} courses in common! Yay! <br>
                                <form action="/"><input type="submit" value="Go back."></form>
                                </body>
                                </html>'''
            for i in common_list:
                result_string += "<br>" + i
            return result_string
        else:
            return '''<!DOCTYPE html>
                    <html>
                    <head>
                        <title>ICal Result :D</title>
                    </head>
                    <body bgcolor="#181a1b" text="#e8e6e3">
                    You have no courses in common. Better luck next sem. :(
                    <form action="/"><input type="submit" value="Go back."></form>
                    </body>
                    </html>'''
    else:
        return redirect(url_for('index'))
        
@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')

@app.route('/savefile/', methods=['POST', 'GET'])
def savefile():
    if request.method == 'POST':
        name = request.form['name'].lower()
        if (name == ""):
            return '''Enter valid username.<form action="/upload"><input type="submit" value="Go back."></form>'''
        file = request.files['sched']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], name + '.ics'))
        return '''<!DOCTYPE html>
                    <html>
                    <head>
                        <title>File Upload Success</title>
                    </head>
                    <body bgcolor="#181a1b" text="#e8e6e3">
                    File successfully added to database.<br>
                    Click button below to go back to home page to compare schedules.
                    <form action="/"><input type="submit" value="Go back."></form>
                    </body>
                    </html>'''
    else:
        return redirect(url_for('index'))
    
@app.route('/incognito/', methods=['POST', 'GET'])
def incognito():
    if request.method == 'GET':
        return render_template('incognito-page.html')
    else:
        sched1 = request.files['sched1']
        sched1.save(os.path.join(app.config['UPLOAD_FOLDER'], 'sched1.ics'))
        sched2 = request.files['sched2']
        sched2.save(os.path.join(app.config['UPLOAD_FOLDER'], 'sched2.ics'))
        g = open(os.path.join(app.config['UPLOAD_FOLDER'], 'sched1.ics'))
        g1 = open(os.path.join(app.config['UPLOAD_FOLDER'], 'sched2.ics'))
        gcal = Calendar.from_ical(g.read())
        gcal1 = Calendar.from_ical(g1.read())

        common = 0
        common_list = []

        for component in gcal.walk():
            for component1 in gcal1.walk():
                if component.name == "VEVENT" and component1.name == "VEVENT":
                    if (component1.get("summary") == component.get('summary')):
                        common += 1
                        common_list.append(component.get('summary').strip('*').split('(')[0])
        g.close()
        g1.close()

        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'sched1.ics'))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'sched2.ics'))

        result_string = ""
        if(common > 0):
            result_string = f'''<!DOCTYPE html>
                                <html>
                                <head>
                                    <title>ICal Result :D</title>
                                </head>
                                <body bgcolor="#181a1b" text="#e8e6e3">
                                You guys have {common} courses in common! Yay! <br>
                                <form action="/"><input type="submit" value="Go back."></form>
                                </body>
                                </html>'''
            for i in common_list:
                result_string += "<br>" + i
            return result_string
        else:
            return '''<!DOCTYPE html>
                    <html>
                    <head>
                        <title>ICal Result :D</title>
                    </head>
                    <body bgcolor="#181a1b" text="#e8e6e3">
                    You have no courses in common. Better luck next sem. :(
                    <form action="/"><input type="submit" value="Go back."></form>
                    </body>
                    </html>'''
        
@app.route('/delete/', methods=['POST', 'GET'])
def delete():
    if request.method == 'GET':
        return render_template('delete-page.html')
    else:
        userid = request.form['name'].lower()
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], userid + '.ics'))
            return redirect(url_for("index"))
        except:
            return f'''<!DOCTYPE html>
                        <html>
                        <head>
                            <title>ICal</title>
                        </head>
                        <body bgcolor="#181a1b" text="#e8e6e3">
                            Schedule for {userid} not found.<br>
                            <form action="/"><input type="submit" value="Go back."></form>
                        </body>
                        </html>
                        '''

if __name__ == '__main__':
    app.run(debug=True)