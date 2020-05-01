from flask import Flask, render_template,request
import pickle
from werkzeug.security import generate_password_hash, check_password_hash


# defining user class
class User:
    def __init__(self, name, password):
        self.name = name
        self.password = generate_password_hash(password)


# extracting database from file
empty_file = False
while not empty_file:
    with open('users', 'rb') as file:
        try:
            users_database = pickle.load(file)
            empty_file = True
        except EOFError:
            with open('users', 'wb') as file:
                pickle.dump([], file)

# extracting schedules from file
empty_file = False
while not empty_file:
    with open('schedules', 'rb') as file:
        try:
            schedule = pickle.load(file)
            empty_file = True
        except EOFError:
            with open('schedules', 'wb') as file:
                pickle.dump([], file)


# to save database every time it is modified
def save_database():
    global users_database
    with open('users', 'wb') as file:
        pickle.dump(users_database, file)


# to save schedules every time it is modified
def save_schedule():
    global schedule
    with open('schedules', 'wb') as file:
        pickle.dump(schedule, file)


app = Flask(__name__)
CURRENT_USER = False


@app.route('/', methods=['post', 'get'])
def landing():
    global CURRENT_USER
    global users_database
    username = False
    password = False
    if request.method == 'POST':
        username = request.form.get('username')  # запрос к данным формы
        password = request.form.get('password')
    if username and password:
        user_found = False
        for i in users_database:
            if i.name == username:
                user_found = True
                if i.check_password(password):
                    CURRENT_USER = i
                    # successful authorization
                    return render_template('app.html', username=username)
                else:
                    # wrong password
                    return render_template('index.html', message='Wrong password', login=True)
        if not user_found:
            return render_template('login.html', message='No such user')
    else:
        return render_template('login.html', message='Type in correct login and password')
    if not CURRENT_USER:
        return render_template('index.html', login=True)
    else:
        return render_template('index.html', user=CURRENT_USER)


@app.route('/reg/', methods=['post', 'get'])
def landing_reg():
    return render_template('index.html', register=True)


if __name__ =='__main__':
    app.run()
