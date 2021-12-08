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
            'product_id TEXT,'
            'title TEXT,'
            'summary TEXT,'
            'footprint_wkt TEXT,'
            'file_size INTEGER,'
            'eumetsat BOOLEAN,'
            'status TEXT'
            ');'
        )
