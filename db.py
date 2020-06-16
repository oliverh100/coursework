import sqlite3
from sqlite3 import Error

database = r"static/activities_database.db"


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)

    except Error as e:
        print(e)


def create_teacher(conn, teacher):
    sql = """
            INSERT INTO teachers (first_name, last_name, initials, email, title)
            VALUES (?,?,?,?,?)
            """
    cur = conn.cursor()
    cur.execute(sql, teacher)
    conn.commit()
    return cur.lastrowid


def create_activity(conn, activity):
    sql = """
            INSERT INTO activities (activity_name, room_id, date_time, max_attendees, food_supplied)
            VALUES (?,?,?,?,?)
            """

    cur = conn.cursor()
    cur.execute(sql, activity)
    conn.commit()
    return cur.lastrowid


def create_room(conn, room):
    sql = """
            INSERT INTO rooms (room_name, building)
            VALUES (?,?)
            """
    cur = conn.cursor()
    cur.execute(sql, room)
    conn.commit()
    return cur.lastrowid


def create_link(conn, link):
    sql = """
                INSERT INTO links (activity_id, teacher_id, in_charge)
                VALUES (?,?,?)
                """
    cur = conn.cursor()
    cur.execute(sql, link)
    conn.commit()
    return cur.lastrowid


def select_all_teachers(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM teachers")
    return cur.fetchall()


def select_teacher(conn, id):
    sql = "SELECT * FROM teachers WHERE teacher_id=?"
    cur = conn.cursor()
    cur.execute(sql, (id,))

    return cur.fetchall()


def update_teacher(conn, teacher):
    sql = """
                UPDATE teachers
                SET first_name=?,
                    last_name=?,
                    initials=?,
                    email=?,
                    title=?
                WHERE teacher_id=?"""
    cur = conn.cursor()
    cur.execute(sql, teacher)
    conn.commit()


def delete_teacher(conn, id):
    sql = 'DELETE FROM teachers WHERE teacher_id=?'
    cur = conn.cursor()

    cur.execute(sql, (id,))
    conn.commit()


def select_all_rooms(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM rooms")

    return cur.fetchall()


def select_room(conn, id):
    sql = "SELECT * FROM rooms WHERE room_id=?"
    cur = conn.cursor()
    cur.execute(sql, (id,))

    return cur.fetchall()


def update_room(conn, room):
    sql = """
                UPDATE rooms
                SET room_name=?,
                    building=?
                WHERE room_id=?"""
    cur = conn.cursor()
    cur.execute(sql, room)
    conn.commit()


def delete_room(conn, id):
    sql = 'DELETE FROM rooms WHERE room_id=?'
    cur = conn.cursor()

    cur.execute(sql, (id,))


def select_all_activities(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM activities")

    results = []

    for activity in cur.fetchall():
        activity_id = activity[0]
        link = select_links(conn, activity_id)
        results = list(activity)
        print(link)
        results.insert(1, link[2])

    return results


def select_activities(conn, id):
    sql = "SELECT * FROM activities WHERE activity_id=?"
    cur = conn.cursor()

    cur.execute(sql, (id,))

    return cur.fetchall()


def update_activity(conn, activity):
    sql = """
                UPDATE activities
                SET activity_name=?,
                    room_id=?,
                    date_time=?,
                    max_attendees=?,
                    food_supplied=?
                WHERE activity_id=?"""

    cur = conn.cursor()

    cur.execute(sql, activity)
    conn.commit()
    return cur.lastrowid


def delete_activity(conn, id):
    sql = 'DELETE FROM activities WHERE activity_id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()


def select_all_links(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM links")

    return cur.fetchall()


def select_links(conn, activity_id):
    sql = "SELECT * FROM links WHERE activity_id=? AND in_charge=1"
    cur = conn.cursor()

    cur.execute(sql, (activity_id,))

    return cur.fetchone()


def create_user(conn, user):
    username = user[0]
    email = user[1]
    hash = user[2]

    results = []

    cur = conn.cursor()
    cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE username=?)", username)
    results.append(cur.fetchone())
    cur.execute("SELECT EXISTS(SELECT 1 FROM users WHERE email=?)", email)
    results.append(cur.fetchone())

    results = [i[0] for i in results]

    if 1 in results:
        raise Exception()


def startup(conn):
    sql_create_teachers_table = """
                                        CREATE TABLE IF NOT EXISTS teachers (
                                        teacher_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                        first_name text NOT NULL,
                                        last_name text NOT NULL,
                                        initials text NOT NULL, 
                                        email text NOT NULL,
                                        title text NOT NULL
                                        );
                                        """

    sql_create_rooms_table = """
                                    CREATE TABLE IF NOT EXISTS rooms (
                                    room_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    room_name text NOT NULL,
                                    building text NOT NULL
                                    );
                                    """

    sql_create_activities_table = """
                                    CREATE TABLE IF NOT EXISTS activities (
                                    activity_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    activity_name text NOT NULL,
                                    room_id integer NOT NULL,
                                    date_time text NOT NULL,
                                    max_attendees integer NOT NULL,
                                    food_supplied bool NOT NULL,
                                    FOREIGN KEY (room_id)
                                        REFERENCES rooms (room_id)
                                        ON UPDATE RESTRICT
                                        ON DELETE RESTRICT
                                    );
                                    """

    sql_create_users_table = """
                                        CREATE TABLE IF NOT EXISTS users (
                                        user_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                        username TEXT NOT NULL,
                                        email TEXT NOT NULL,
                                        hash TEXT NOT NULL
                                        );
                                        """

    sql_create_links_table = """
                                CREATE TABLE IF NOT EXISTS links (
                                link_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                activity_id integer NOT NULL,
                                teacher_id integer NOT NULL,
                                in_charge bool NOT NULL,
                                FOREIGN KEY (activity_id)
                                    REFERENCES activities (activity_id)
                                    ON UPDATE RESTRICT
                                    ON DELETE RESTRICT,
                                FOREIGN KEY (teacher_id)
                                    REFERENCES teachers (teacher_id)
                                    ON UPDATE RESTRICT
                                    ON DELETE RESTRICT
                                );
                                """

    if conn is not None:
        create_table(conn, sql_create_rooms_table)
        create_table(conn, sql_create_teachers_table)
        create_table(conn, sql_create_activities_table)
        create_table(conn, sql_create_users_table)


def main():
    database = r"static/activities_database.db"

    sql_create_teachers_table = """
                                    CREATE TABLE IF NOT EXISTS teachers (
                                    teacher_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    first_name text NOT NULL,
                                    last_name text NOT NULL,
                                    initials text NOT NULL, 
                                    email text NOT NULL,
                                    title text NOT NULL
                                    );
                                    """

    sql_create_rooms_table = """
                                CREATE TABLE IF NOT EXISTS rooms (
                                room_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                room_name text NOT NULL,
                                building text NOT NULL
                                );
                                """

    sql_create_activities_table = """
                                CREATE TABLE IF NOT EXISTS activities (
                                activity_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                activity_name text NOT NULL,
                                room_id integer NOT NULL,
                                date_time text NOT NULL,
                                max_attendees integer NOT NULL,
                                food_supplied bool NOT NULL,
                                FOREIGN KEY (room_id)
                                    REFERENCES rooms (room_id)
                                    ON UPDATE RESTRICT
                                    ON DELETE RESTRICT
                                );
                                """

    sql_create_users_table = """
                                    CREATE TABLE IF NOT EXISTS users (
                                    user_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    username TEXT NOT NULL,
                                    email TEXT NOT NULL,
                                    hash TEXT NOT NULL
                                    );
                                    """

    sql_create_links_table = """
                                CREATE TABLE IF NOT EXISTS links (
                                link_id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                activity_id integer NOT NULL,
                                teacher_id integer NOT NULL,
                                in_charge bool NOT NULL,
                                FOREIGN KEY (activity_id)
                                    REFERENCES activities (activity_id)
                                    ON UPDATE RESTRICT
                                    ON DELETE RESTRICT,
                                FOREIGN KEY (teacher_id)
                                    REFERENCES teachers (teacher_id)
                                    ON UPDATE RESTRICT
                                    ON DELETE RESTRICT
                                );
                                """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_rooms_table)
        create_table(conn, sql_create_teachers_table)
        create_table(conn, sql_create_activities_table)
        # create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_links_table)

    else:
        print('Error! cannot create the database connection')

    with conn:
        # print(select_all_teachers(conn))
        # print(select_all_rooms(conn))

        t1 = ('Andrew', 'Dales', 'AD', 'andrew.dales@highgateschool.org.uk', 'Mr')
        t2 = ('Daryl', 'Noyce', 'DJN', 'daryl.noyce@highgateschool.org.uk', 'Mr')
        t3 = ('Anson', 'Cheung', 'ACC', 'anson.cheung@highgateschool.org.uk', 'Dr')

        r1 = ('CB5', 'Charter Building')
        r2 = ('9', 'Central Hall')
        r3 = ('SBR3', 'Science Block Roof')

        a1 = ('Chess', 1, 'TuesLunch', 12, True)
        a2 = ('Puzzle', 3, 'WedLunch', 6, False)

        l1 = (1, 1, True)
        l2 = (1, 2, False)
        l3 = (2, 2, True)

        # create_teacher(conn, t1)
        # create_teacher(conn, t2)
        # create_teacher(conn, t3)
        #
        # create_room(conn, r1)
        # create_room(conn, r2)
        # create_room(conn, r3)
        #
        # create_activity(conn, a1)
        # create_activity(conn, a2)
        #
        # create_link(conn, l1)
        # create_link(conn, l2)
        # create_link(conn, l3)

        # create_activity(conn, ('Chess', 4, 'TuesLunch', 12, True))


if __name__ == '__main__':
    main()
