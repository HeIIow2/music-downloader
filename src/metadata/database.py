import sqlite3
import os
import logging

logging.basicConfig(level=logging.DEBUG)

def get_temp_dir():
    import tempfile

    temp_folder = "music-downloader"
    temp_dir = os.path.join(tempfile.gettempdir(), temp_folder)
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir

DATABASE_STRUCTURE_FILE = "src/metadata/database_structure.sql"
TEMP_DIR = get_temp_dir()
DATABASE_FILE = "metadata.db"
db_path = os.path.join(TEMP_DIR, DATABASE_FILE)

sqliteConnection = sqlite3.connect(db_path)
cursor = sqliteConnection.cursor()

def init_db(cursor, reset_anyways: bool = False):
    # check if db exists
    exists = True
    try:
        query = 'SELECT * FROM track;'
        cursor.execute(query)
        _ = cursor.fetchall()
    except sqlite3.OperationalError:
        exists = False
    
    if not exists:
        logging.info("Database does not exist yet.")

    if reset_anyways or not exists:
        # reset the database if reset_anyways is true or if an error has been thrown previously.
        logging.info("Creating/Reseting Database.")

        # read the file
        with open(DATABASE_STRUCTURE_FILE, "r") as database_structure_file:
            query = database_structure_file.read()
            cursor.executescript(query)

init_db(cursor=cursor)

if __name__ == "__main__":
    pass
