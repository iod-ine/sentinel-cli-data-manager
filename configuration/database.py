""" Handle the database. """

import sqlite3

import configuration.paths as paths


def generate_metadata_database():
    """ Generate a new metadata database. """

    paths.database.unlink(missing_ok=True)

    with sqlite3.connect(paths.database) as con:
        cur = con.cursor()

        cur.execute(
            'CREATE TABLE metadata('
            'product_id TEXT PRIMARY KEY,'
            'title TEXT UNIQUE,'
            'footprint_wkt TEXT,'
            'file_size INTEGER,'
            'eumetsat BOOLEAN,'
            'status TEXT'
            ');'
        )


def get_entry_by_id(id_):
    """ Return the entry with the specified product ID. """

    with sqlite3.connect(paths.database) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM metadata WHERE product_id = ?;', (id_,))
        result = cursor.fetchone()

    return result


def get_entry_by_name(name):
    """ Return the entry with the specified product title. """

    with sqlite3.connect(paths.database) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM metadata WHERE title = ?;', (name,))
        result = cursor.fetchone()

    return result
