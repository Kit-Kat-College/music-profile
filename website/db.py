import sqlite3

def init_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            DOB DATE NOT NULL,
            email TEXT NOT NULL UNIQUE,
            hashed_pw TEXT NOT NULL,
            profile_picture TEXT NOT NULL
        )
    ''')

    # Create Albums table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Albums (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            creator TEXT NOT NULL,
            creation_date DATE NOT NULL,
            cover TEXT NOT NULL,
            track_count INTEGER NOT NULL,
            added_by INTEGER NOT NULL,
            
            FOREIGN KEY (added_by) REFERENCES Users(id)
                ON DELETE CASCADE
        )
    ''')

    # Create SavedAlbums table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SavedAlbums (
            savedalbum_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            album_id INTEGER NOT NULL,
            
            FOREIGN KEY (user_id) REFERENCES Users(id)
                ON DELETE CASCADE,

            FOREIGN KEY (album_id) REFERENCES Albums(id)
                ON DELETE CASCADE
        )
    ''')

    connection.commit() # Commit changes to SQ
    connection.close()

def db_connection():
    connection = sqlite3.connect("database.db")

    # Enable foreign key enforcement in SQLite
    connection.execute("PRAGMA foreign_keys = ON")

    # Return query results as rows that can be accessed by column name
    connection.row_factory = sqlite3.Row

    return connection

# -----------------------------------------------
# ? placeholders safely insert the supplied values
# -----------------------------------------------

def insert_user(signUsername, signDOB, signEmail, pw_hashed, profile_pfp):
    connection = db_connection()

    # Insert new user into the database
    connection.execute("""
        INSERT INTO Users (username, DOB, email, hashed_pw, profile_picture)
        VALUES (?, ?, ?, ?, ?)
    """, (signUsername, signDOB, signEmail, pw_hashed, profile_pfp))

    connection.commit()
    connection.close()


def gather_user_info(key):
    connection = db_connection()

    # Find the user matching the supplied username
    user_data = connection.execute("""
        SELECT *
        FROM Users
        WHERE username = ?
    """, (key,)).fetchone()

    connection.close()
    return user_data


def insert_album(aiTitle, aiCreator, aiCreation_date, cover_path, aiTrack_count, user_id):
    connection = db_connection()

    # Insert new album into the database
    connection.execute("""
        INSERT INTO Albums (title, creator, creation_date, cover, track_count, added_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (aiTitle, aiCreator, aiCreation_date, cover_path, aiTrack_count, user_id))

    connection.commit()
    connection.close()


def gather_album_info(key1, key2):
    connection = db_connection()

    # Find the album matching the supplied title & creator
    album_data = connection.execute("""
        SELECT *
        FROM Albums
        WHERE title = ?
        AND creator = ?
    """, (key1, key2)).fetchone()

    connection.close()
    return album_data

def check_if_album_is_registered(ui_title, ui_creator):
    connection = db_connection()

    album_id = connection.execute("""
        SELECT id
        FROM Albums
        WHERE title = ?
        AND creator = ?
    """, (ui_title, ui_creator)).fetchone()

    connection.close()

    if album_id is None:
        return None

    return album_id["id"]


def change_album_cover(cover_path, new_album_id):
    connection = db_connection()
    connection.execute("""
        UPDATE Albums
        SET cover = ?
            WHERE id = ?
    """, (cover_path, new_album_id))
    connection.commit()
    connection.close()


def change_username(newUsername, user_id):
    connection = db_connection()
    connection.execute("""
        UPDATE Users
        SET username = ?
            WHERE id = ?
        """, (newUsername, user_id))
    connection.commit()
    connection.close()

def change_email(newEmail, user_id):
    connection = db_connection()
    connection.execute("""
        UPDATE Users
        SET email = ?
            WHERE id = ?
        """, (newEmail, user_id))
    connection.commit()
    connection.close()

def gather_user_password(user_id):
    connection = db_connection()

    password_hash = connection.execute("""
        SELECT hashed_pw
        FROM Users
        WHERE id = ?
    """, (user_id,)).fetchone()

    connection.close()

    return password_hash["hashed_pw"]

def change_pw_hash(newPw_hash, user_id):
    connection = db_connection()
    connection.execute("""
        UPDATE Users
        SET hashed_pw = ?
            WHERE id = ?
        """, (newPw_hash, user_id))
    connection.commit()
    connection.close()



def change_user_pfp(pfp_path, session):
    connection = db_connection()
    connection.execute("""
        UPDATE Users
        SET profile_picture = ?
            WHERE username = ?
        """, (pfp_path, session))
    connection.commit()
    connection.close()


def gather_user_id(username):
    connection = db_connection()
    user_id = connection.execute("""
        SELECT id
        FROM Users
            WHERE username = ?
    """, (username,)).fetchone()

    connection.close()
    return user_id["id"]

def update_saved_records(session, album_id):
    connection = db_connection()

    # Find the user's ID using their username
    user = connection.execute("""
        SELECT id
        FROM Users
        WHERE username = ?
    """, (session,)).fetchone()

    if user is not None:

        # Save the album for this user
        # INSERT OR IGNORE prevents the same album
        # from being saved twice by the same user.
        connection.execute("""
            INSERT OR IGNORE INTO SavedAlbums (user_id, album_id)
            VALUES (?, ?)
        """, (user["id"], album_id))

        connection.commit()

    connection.close()


def user_saved_albums(session):
    connection = db_connection()

    # Get all album IDs saved by the current user
    rows = connection.execute("""
        SELECT SavedAlbums.album_id
        FROM SavedAlbums
        JOIN Users
            ON SavedAlbums.user_id = Users.id
        WHERE Users.username = ?
    """, (session,)).fetchall()

    connection.close()

    # Return the album IDs as a normal Python list
    return [row["album_id"] for row in rows]


def gather_saved_album_data(saved_album_ids):
    connection = db_connection()

    if not saved_album_ids:
        connection.close()
        return []

    placeholders = ", ".join("?" for _ in saved_album_ids)

    saved_album_data = connection.execute(
        f"""
        SELECT *
        FROM Albums
        WHERE id IN ({placeholders})
        """,
        saved_album_ids
    ).fetchall()

    connection.close()

    # Put albums back into the same order as saved_album_ids
    album_by_id = {album["id"]: album for album in saved_album_data}

    return [album_by_id[album_id] for album_id in saved_album_ids]

def check_if_album_is_saved(session, album_id):
    # Open a connection to the database
    connection = db_connection()

    # Check if the current user has saved the specified album
    saved_album = connection.execute("""
        SELECT SavedAlbums.savedalbum_id
        FROM SavedAlbums

        JOIN Users
            ON SavedAlbums.user_id = Users.id
        WHERE Users.username = ?
        AND SavedAlbums.album_id = ?
    """, (session, album_id)).fetchone()

    connection.close()

    # The album has not been saved by this user
    if saved_album is None:
        return False

    # The album has already been saved
    else:
        return True


def delete_album(album_id, user_id):
    connection = db_connection()

    connection.execute("""
        DELETE FROM Albums
        WHERE id = ?
        AND added_by = ?
    """, (album_id, user_id))

    connection.commit()
    connection.close()

def delete_user(user_id, session):
    connection = db_connection()
    connection.execute("""
        DELETE FROM Users
            WHERE id = ?
                AND username = ?
        """, (user_id, session))

    connection.commit()
    connection.close()

def gather_current_user_pfp(session):
    connection = db_connection()
    user = connection.execute("""
        SELECT profile_picture
        FROM Users
            WHERE username = ?
        """, session).fetchone()

    connection.close()
    return user["profile_picture"]

def console():
    connection = db_connection()

    result = connection.execute("""
        DELETE FROM Users
            WHERE id = ?
    """, ("3"))

    print("Rows Affected:", result.rowcount)

    connection.commit()
    connection.close()



