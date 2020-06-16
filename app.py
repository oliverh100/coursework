from flask import Flask, render_template, request, redirect, flash, url_for
from flask_caching import Cache
import db


def startup_database():
    global conn
    conn = db.create_connection(db.database)
    db.startup(conn)
    with conn:
        db.select_all_teachers(conn)


config = {
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 300
}
app = Flask(__name__)
app.secret_key = '\xb2\x86z\xe0>\xbc\xd8\x9e\xc1\x1c\x17\xbc'
app.before_first_request(startup_database)
app.static_folder = 'static'
tables = {}
conn = None
app.config.from_mapping(config)
cache = Cache(app)


@app.route('/home/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def home():
    data = request.form

    if 'teachers' in data:
        return redirect(url_for('teachers'))

    elif 'rooms' in data:
        return redirect(url_for('rooms'))

    elif 'activities' in data:
        return redirect(url_for('activities'))

    return render_template('home.html')


def get_table():
    global tables
    with conn:
        tables['teachers'] = db.select_all_teachers(conn)
        tables['rooms'] = db.select_all_rooms(conn)
        tables['activities'] = db.select_all_activities(conn)


def check_id(data, key, category):
    entry_id_temp = data[key]
    id_list = [str(i[0]) for i in tables[category]]
    if entry_id_temp not in id_list:
        alert = 'Invalid ID'
        flash(alert)
        return 0
    else:
        return entry_id_temp


@app.route('/teachers/', methods=['GET', 'POST'])
def teachers():
    get_table()
    data = request.form

    if 'add' in data:
        return render_template('teachers.html', table=tables['teachers'], add_options=True)

    elif 'submit_add' in data:
        teacher_file = [data['first_name'], data['last_name'], data['initials'], data['email'], data['title']]
        with conn:
            db.create_teacher(conn, teacher_file)
        get_table()
        return render_template('teachers.html', table=tables['teachers'])

    elif 'edit' in data:
        return render_template('teachers.html', table=tables['teachers'], edit_id_options=True)

    elif 'submit_edit_id' in data:
        if not (teacher_edit_id := check_id(data, 'edit_id', 'teachers')):
            return render_template('teachers.html', table=tables['teachers'], edit_id_options=True)
        else:
            cache.set('teacher_edit_id', teacher_edit_id)
            with conn:
                teacher_update = db.select_teacher(conn, teacher_edit_id)[0]
            return render_template('teachers.html', table=tables['teachers'], edit_options=True, teacher_file=teacher_update)

    elif 'submit_edit' in data:
        teacher_edit_id = cache.get('teacher_edit_id')
        teacher_update = [data['first_name'], data['last_name'], data['initials'], data['email'], data['title'], teacher_edit_id]
        with conn:
            db.update_teacher(conn, teacher_update)
        get_table()
        return render_template('teachers.html', table=tables['teachers'])

    elif 'delete' in data:
        return render_template('teachers.html', table=tables['teachers'], delete_options=True)

    elif 'submit_delete' in data:
        if not (teacher_delete_id := check_id(data, 'delete_id', 'teachers')):
            return render_template('teachers.html', table=tables['teachers'], delete_options=True)
        else:
            with conn:
                try:
                    db.delete_teacher(conn, teacher_delete_id)
                except Exception:
                    alert = 'Teacher is present in activities'
                    flash(alert)
            get_table()
            return render_template('teachers.html', table=tables['teachers'])

    elif 'back' in data:
        return redirect(url_for('home'))

    return render_template('teachers.html', table=tables['teachers'])


@app.route('/rooms/', methods=['GET', 'POST'])
def rooms():
    get_table()
    data = request.form

    if 'add' in data:
        return render_template('rooms.html', table=tables['rooms'], add_options=True)

    elif 'submit_add' in data:
        room_file = [data['room_name'], data['building']]
        with conn:
            db.create_room(conn, room_file)
        get_table()
        return render_template('rooms.html', table=tables['rooms'])

    elif 'edit' in data:
        return render_template('rooms.html', table=tables['rooms'], edit_id_options=True)

    elif 'submit_edit_id' in data:
        if not (room_edit_id := check_id(data, 'edit_id', 'rooms')):
            return render_template('rooms.html', table=tables['rooms'], edit_id_options=True)
        else:
            cache.set('room_edit_id', room_edit_id)
            with conn:
                room_update = db.select_room(conn, room_edit_id)[0]
            return render_template('rooms.html', table=tables['rooms'], edit_options=True, room_file=room_update)

    elif 'submit_edit' in data:
        room_edit_id = cache.get('room_edit_id')
        room_update = [data['room_name'], data['building'], room_edit_id]
        with conn:
            db.update_room(conn, room_update)
        get_table()
        return render_template('rooms.html', table=tables['rooms'])

    elif 'delete' in data:
        return render_template('rooms.html', table=tables['rooms'], delete_options=True)

    elif 'submit_delete' in data:
        if not (room_delete_id := check_id(data, 'delete_id', 'rooms')):
            return render_template('rooms.html', table=tables['rooms'], delete_options=True)
        else:
            with conn:
                try:
                    db.delete_room(conn, room_delete_id)
                except Exception:
                    alert = 'Room is used in activities'
                    flash(alert)
            get_table()
            return render_template('rooms.html', table=tables['rooms'])

    elif 'back' in data:
        return redirect(url_for('home'))

    return render_template('rooms.html', table=tables['rooms'])


@app.route('/activities/', methods=['GET', 'POST'])
def activities():
    data = request.form
    get_table()
    print(tables['activities'])

    if 'add' in data:
        return render_template('activities.html', table=tables['activities'], add_options=True, activity_file=[])

    elif 'submit_add' in data:
        activity_file = [data['activity_name'], data['teacher_in_charge_id'], data['teacher_list_id'], data['room_id'], data['datetime'], data['max_attendees'], data['food_supplied']]
        with conn:
            try:
                db.create_activity(conn, activity_file)
            except Exception:
                cache.set('activity_add_file', activity_file)
                alert = 'Invalid teacher or room ID'
                flash(alert)
                return render_template('activities.html', table=tables['activities'], add_options=True, activity_file=[0] + cache.get('activity_add_file'))
        get_table()
        return render_template('activities.html', table=tables['activities'])

    elif 'edit' in data:
        return render_template('activities.html', table=tables['activities'], edit_id_options=True)

    elif 'submit_edit_id' in data:
        if not (activity_edit_id := check_id(data, 'edit_id', 'activities')):
            return render_template('activities.html', table=tables['activities'], edit_id_options=True)
        else:
            cache.set('activity_edit_id', activity_edit_id)
            with conn:
                activity_update = db.select_activities(conn, activity_edit_id)[0]
            return render_template('activities.html', table=tables['activities'], edit_options=True, activity_file=activity_update)

    elif 'submit_edit' in data:
        activity_edit_id = cache.get('activity_edit_id')
        activity_update = [data['activity_name'], data['teacher_in_charge_id'], data['teacher_list_id'], data['room_id'], data['datetime'], data['max_attendees'], data['food_supplied'], activity_edit_id]
        with conn:
            try:
                db.update_activity(conn, activity_update)
            except Exception:
                cache.set('activity_add_file', activity_update)
                alert = 'Invalid teacher or room ID'
                flash(alert)
                return render_template('activities.html', table=tables['activities'], edit_options=True, activity_file=activity_update)
        get_table()
        return render_template('activities.html', table=tables['activities'])

    elif 'delete' in data:
        return render_template('activities.html', table=tables['activities'], delete_options=True)

    elif 'submit_delete' in data:
        if not (activity_delete_id := check_id(data, 'delete_id', 'activities')):
            return render_template('activities.html', table=tables['activities'], delete_options=True)
        else:
            with conn:
                db.delete_activity(conn, activity_delete_id)
            get_table()
            return render_template('activities.html', table=tables['activities'])

    elif 'back' in data:
        return redirect(url_for('home'))

    return render_template('activities.html', table=tables['activities'])


if __name__ == '__main__':
    app.run(host='0.0.0.0')
