import sqlite3

db_filename = 'electricity.sqlite3'


def set_db_filename(filename):
    db_filename = filename

def init_db():
    if not os.path.isfile(db_filename):
        # Схема таблицы подписок
        try:
            connection = create_connection()
            connection.execute('''CREATE TABLE "Subscriptions" (
                "Id"	TEXT NOT NULL UNIQUE,
                "ChatId"	INTEGER NOT NULL,
                "Text"	TEXT NOT NULL,
                "RegionCode"	INTEGER NOT NULL,
                "CreatedAt"	TEXT NOT NULL DEFAULT '',
                PRIMARY KEY("Id")
            );''')
            connection.execute('''CREATE TABLE "Blackouts" (
                "Id"	TEXT NOT NULL UNIQUE,
                "RegionCode"	INTEGER NOT NULL,
                "District"	TEXT NOT NULL,
                "Place"	TEXT,
                "Address"	TEXT,
                "BeginDate"	TEXT NOT NULL,
                "EndDate"	TEXT NOT NULL,
                PRIMARY KEY("Id")
            );''')
        except sqlite3.DatabaseError as e:
            print("DB Error: ", err)
        finally:
            connection.close()

def create_connection(filename=db_filename):
    try:
        return sqlite3.connect(filename)
    except sqlite3.DatabaseError as e:
        print("DB Error: ", err)
        return None


def select(sql, args=tuple()):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(sql, args)
        return cursor.fetchall()
    except sqlite3.DatabaseError as err:
        print("DB Error: ", err)
        return None
    finally:
        connection.close()


def insert_or_update(sql, args):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(sql, args)
        connection.commit()
        return True
    except sqlite3.DatabaseError as err:
        print("DB Error: ", err)
        return False
    finally:
        connection.close()
