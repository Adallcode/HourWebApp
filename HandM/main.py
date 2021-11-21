from flask import Flask, render_template, session, request, url_for, redirect
from data import analize_signin_data, analize_signup_data, add_hours, get_view_data, Subtract_hours, get_user_name, reset_week_hour_minute, delete_account
from decorators import check_login


app = Flask(__name__)

#Dict with the data for my database

app.config['dbconfig'] = {
    'host': '127.0.0.1',
    'user': 'hourweb',
    'password': 'hourwebpasswd',
    'database': 'hour',
}

'''Set the secret key'''

app.secret_key = 'argp88adhnjdffghjfdrrttg542'


'''Home url'''

@app.route('/home')
@check_login
def home_page()-> str:
    userName = get_user_name(session['email'], app.config['dbconfig'])

    # Update the last and current week hours  whenever a new week start
    reset_week_hour_minute(session['email'], app.config['dbconfig'])

    return render_template('home.html', the_title='Home',  person_name=userName)


'''Add hrs url'''

@app.route('/addHour', methods=['POST', 'GET'])
@check_login
def add_hour() -> str:

    # Update the last and current week hours  whenever a new week start
    reset_week_hour_minute(session['email'], app.config['dbconfig'])

    if request.method == 'POST':
        hour = request.form['hours']
        minute = request.form['minutes']

        '''Before anything convert the input to integer'''
        hour = int(hour)
        minute = int(minute)
        add_hours(hour, minute, app.config['dbconfig'], session['email'])
    
    userName = get_user_name(session['email'], app.config['dbconfig'])

    return render_template('addHour.html', the_title= 'Add hour', person_name=userName)


'''Subtract hrs url'''

@app.route('/subtractHour', methods=['POST', 'GET'])
@check_login
def subtract_hour() -> str:

    # Update the last and current week hours  whenever a new week start
    reset_week_hour_minute(session['email'], app.config['dbconfig'])

    if request.method == 'POST':
        hour = request.form['hours']
        minute = request.form['minutes']

        '''Before anything convert the input to integer'''
        hour = int(hour)
        minute = int(minute)

        #This funtion's name has a (s) at the end
        Subtract_hours(hour, minute, app.config['dbconfig'], session['email'])

    userName = get_user_name(session['email'], app.config['dbconfig'])

    return render_template('subtractHour.html', the_title= 'Subtract hour', person_name=userName)



'''view total hours url'''

@app.route('/viewHour')
@check_login
def total_hour() -> str:

    # Update the last and current week hours  whenever a new week start
    reset_week_hour_minute(session['email'], app.config['dbconfig'])

    res = get_view_data(session['email'], app.config['dbconfig'])

    table_title = ('Last week hours', 'Last week minutes', 'Current week hours', 'Current week minutes',
    'Total hours', 'Total minutes')

    userName = get_user_name(session['email'], app.config['dbconfig'])

    return render_template('viewHour.html', the_title='View_hour', table_column=table_title, 
    person_name= userName, view_data=res )



'''Sign in url'''

@app.route('/')
@app.route('/signin', methods=['POST', 'GET'])
def signin() -> str:

    if request.method == 'POST':
        if analize_signin_data(request.form['email'], request.form['passwd'], app.config['dbconfig']):
            
            #First log in the user
            session['log_in'] = 'log_in'
            session['email'] = request.form['email']
            return redirect("/home")

    return render_template('signin.html', the_title='Sign in', page_title='Sign in')



'''Sign up url'''

@app.route('/signup', methods=['POST', 'GET'])
def signup() -> str:

    #Clear the msg in flash before anything
    session.pop( '_flashes', None)

    if request.method == 'POST':
        name = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        passwd = request.form['passwd']
        passwd2 = request.form['passwd2']

        #Take care to add the user data into the database whenever the data is correct
        if analize_signup_data(name, lname, email, passwd, passwd2, app.config['dbconfig']):
            return redirect(url_for("signin"))


    return render_template('signup.html', the_title='Sign up', page_title='Sign up')



'''Delete account url'''

@app.route('/delete', methods=['POST', 'GET'])
@check_login
def delete():

    if request.method == 'POST':

        # The request can't be empty
        if not request.form:
            return render_template('delete.html', the_title= 'Delete')
        else:

            decision = request.form['decision']

            if delete_account(session['email'], app.config['dbconfig'], decision):
                return redirect( url_for('logout'))
            else:
                return redirect('home')


    return render_template('delete.html', the_title= 'Delete')



'''Log out url'''
'''When the user is logged in and want to quit the app, than pop the key'''

@app.route('/logout')
def logout():

    session.pop('log_in')
    session.pop('email')
    return redirect(url_for("signin"))


if __name__ == '__main__':
    app.run(debug=True)