import sqlite3
from datetime import datetime

import click
from flask import current_app, g

def getDb():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def closeDb(e=None):
    db = g.pop('db',None)

    if db is not None:
        db.close()

def initDb():
    db = getDb()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def initDbCommand():
    """Clear data and create tables"""
    initDb()
    click.echo('Initialized the db')

sqlite3.register_converter(
    'timestamp',lambda v: datetime.fromisoformat(v.decode())
)

def initApp(app):
    app.teardown_appcontext(closeDb)
    app.cli.add_command(initDbCommand)

