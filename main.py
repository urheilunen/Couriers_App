from flask import Flask, render_template,request
import pickle
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


# defining user class
class User:
    def __init__(self, name, password):
        self.name = name
        self.password = generate_password_hash(password)

    def check_password(self, password_to_be_checked):
        return check_password_hash(self.password, password_to_be_checked)


# defining schedule classes
class Day:
    def __init__(self, date):
        self.date = date
        self.shifts = [
            [[None, None], [None]],
            [[None], [None]],
            [[None], [None]],
            [[None], [None]],
            [[None], [None]]
        ]

    def __str__(self):
        info = str(self.date)
        for i in self.shifts:
            info += '\n' + str(i)
        return info


class Week:
    def __init__(self, begin_date=datetime.datetime.today().date()):
        self.begin_date = begin_date
        while self.begin_date.isoweekday() != 1:
            self.begin_date += datetime.timedelta(days=1)
        self.end_date = self.begin_date + datetime.timedelta(days=6)
        self.schedule = [
            Day(self.begin_date),
            Day(self.begin_date + datetime.timedelta(days=1)),
            Day(self.begin_date + datetime.timedelta(days=2)),
            Day(self.begin_date + datetime.timedelta(days=3)),
            Day(self.begin_date + datetime.timedelta(days=4)),
            Day(self.begin_date + datetime.timedelta(days=5)),
            Day(self.begin_date + datetime.timedelta(days=6))
        ]
        self.is_approved = False

    def approve(self):
        self.is_approved = True

    def get_date(self):
        return str(self.begin_date.strftime('%d/%m/%Y')) + '-' + str(self.end_date.strftime('%d/%m/%Y'))

    # restaurant 0-4: pf-kt
    # shift 0/1: morning/evening
    def add_vacancy(self, day, restaurant, shift):
        self.schedule[day].shifts[restaurant][shift].append(None)

    def remove_vacancy(self, day, restaurant, shift):
        self.schedule[day].shifts[restaurant][shift].remove(None)

    def __str__(self):
        for i in self.schedule:
            print(i)


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


schedule.append(Week(begin_date=datetime.datetime.today().date() - datetime.timedelta(days=7)))
schedule.append(Week())

app = Flask(__name__)
current_user = False


@app.route('/', methods=['post', 'get'])
def landing():
    global current_user
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
                    current_user = i
                    # successful authorization
                    return render_template('user_menu.html', username=username)
                else:
                    # wrong password
                    return render_template('index.html', message='Wrong password', login=True)
        if not user_found:
            return render_template('index.html', message='No such user', login=True)
    else:
        return render_template('index.html', login=True)
    # if not CURRENT_USER:
    #     return render_template('index.html', login=True)
    # else:
    #     return render_template('index.html', user=CURRENT_USER)


@app.route('/reg/', methods=['post', 'get'])
def landing_reg():
    global users_database
    username = False
    password1 = False
    password2 = False
    if request.method == 'POST':
        username = request.form.get('username')  # запрос к данным формы
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

    if username and password1 and password2:
        if password1 == password2:
            # input users_data alright, begin working with database
            user_found = False
            for i in users_database:
                if i.name == username:
                    user_found = True
                    break
            if not user_found:
                users_database.append(User(username, password1))
                save_database()
                return render_template('index.html', message='Successfully registered!', login=True)
            else:
                return render_template('index.html', message='User already exists', register=True)
        else:
            return render_template('index.html', message="Passwords don't match!", register=True)
    else:
        return render_template('index.html', register=True)


@app.route('/schedule/', methods=['post', 'get'])
def schedule_app():
    global schedule
    global current_user
    time_now = datetime.datetime.today().time()
    time_6pm = time_now.replace(hour=18, minute=0, second=0)
    if datetime.datetime.today().isoweekday() == 7 and time_now > time_6pm:
        if Week().begin_date != schedule[-1].begin_date:
            schedule.append(Week())
    week = schedule[-1]
    restaurant = False
    if request.method == 'POST':
        restaurant = request.form.get('restaurant')

    if restaurant:
        print(restaurant)
        return render_template('app.html', current_user=current_user, week=week, restaurant_selected=True)
    return render_template('app.html', current_user=current_user, week=week)


@app.route('/logout/')
def logout():
    global current_user
    current_user = False
    return render_template('logout.html')


if __name__ == '__main__':
    app.run()
