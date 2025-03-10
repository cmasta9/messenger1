from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from messenger2.auth import loginReq
from messenger2.db import getDb

bp = Blueprint('message', __name__)

@bp.route('/')
def index():
    db = getDb()
    messages = db.execute(
        "SELECT p.id, body, created, author_id, author"
        " FROM message p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template('message/index.html', messages=messages)

@bp.route('/', methods=('GET', 'POST'))
@loginReq
def create():
    if request.method == 'POST':
        body = request.form['body']
        un = g.user['username']
        error = None

        if not body:
            error = 'You must type something'

        if error is not None:
            flash(error)
        else:
            print(un)
            db = getDb()
            db.execute(
                "INSERT INTO message (author_id, author, body) VALUES (?, ?, ?)",
                (g.user['id'], un, body),
            )
            db.commit()
            return redirect(url_for('message.index'))

    return render_template('message/index.html')

def getPost(id, checkAuth=True):
    post = getDb().execute(
        "SELECT p.id, body, created, author_id, author"
        " FROM message p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?",
        (id,),
    ).fetchone()

    if post is None:
        abort(404, f"Message id {id} doesn't exist.")

    if checkAuth and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@loginReq
def update(id):
    post = getPost(id)

    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'You must type something'

        if error is not None:
            flash(error)
        else:
            db = getDb()
            db.execute(
                "UPDATE message SET body = ? WHERE id = ?", (body, id)
            )
            db.commit()
            return redirect(url_for('message.index'))

    return render_template('message/update.html', message=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@loginReq
def delete(id):
    getPost(id)
    db = getDb()
    db.execute('DELETE FROM message WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('message.index'))