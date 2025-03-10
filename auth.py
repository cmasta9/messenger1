import functools
from flask import (Blueprint,flash,g,redirect,render_template,request,session,url_for)
from werkzeug.security import (generate_password_hash,check_password_hash)

from messenger1.db import getDb

bp = Blueprint('auth',__name__,url_prefix='/auth')

@bp.route('/register',methods=('GET','POST'))
def register():
    if request.method == 'POST':
        un = request.form['un']
        pasw = request.form['pass']
        db = getDb()
        error = None

        if not un:
            error = 'username was not provided'
        elif not pasw:
            error = 'password was not provided'

        if not error:
            try:
                db.execute('INSERT INTO user (username,password) VALUES (?,?)',
                           (un, generate_password_hash(pasw)),
                           )
                db.commit()
            except db.IntegrityError:
                error = f'Username {un} is already registered'
            else:
                return redirect(url_for('auth.login'))
            
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login',methods=('POST','GET'))
def login():
    if request.method == 'POST':
        un = request.form['un']
        pasw = request.form['pass']
        db = getDb()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',(un,),
        ).fetchone()

        if user is None:
            error = 'Username does not exist'
        elif not check_password_hash(user['password'],pasw):
            error = 'Password is not correct'

        if error is None:
            session.clear()
            session['uid'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@bp.before_app_request
def loadLogged():
    uid = session.get('uid')

    if uid is None:
        g.user = None
    else:
        g.user = getDb().execute(
            'SELECT * FROM user WHERE id = ?',(uid,)
        ).fetchone()

def loginReq(view):
    @functools.wraps(view)
    def wrapper(**kwargs):
        if g.user is None:
            return redirect('auth.login')
        
        return view(**kwargs)
    return wrapper
