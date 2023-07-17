from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import and_,or_

from Another_eye import app, db
from Another_eye.models import User, Movie


@app.route('/' , methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        year  = request.form.get('year')
        if not year or not title or len(title) > 60 or len(year) != 4:
            flash('Invalid input.')
            return redirect(url_for('index'))
        movie = Movie(title = title , year = year)
        db.session.add(movie)
        db.session.commit()
        flash("Item created.")
        return  redirect(url_for('index'))
    movies = Movie.query.all()
    return render_template('index.html', movies= movies)


@app.route('/about')
def aboutMe():
    return render_template('about.html')


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input')
            return redirect(url_for('login'))
        user = User.query.first()

        if user.username == username and user.validate_password(password):
            login_user(user)
            flash('Login Success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html')

def valid_register(username,IsCityAdmin):
    user = User.query.filter(and_(username==User.username,IsCityAdmin==User.name)).first()
    if user :
        return False
    else:
        return True


@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        identity = request.form['IsAdmin']

        if not username or not password or not confirm_password or not identity:
            flash('Invalid input.')
            return redirect(url_for('register'))
        elif password != confirm_password:
            flash('两次密码不相同！')
            return redirect(url_for('register'))
        elif valid_register(username,identity):
            user = User(name=identity,username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('成功注册')
            return redirect(url_for('login'))
        else:
            flash('该用户已经被注册！')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Good Bye!')
    return redirect(url_for('index'))

#编辑条目
@app.route('/movie/edit/<int:movie_id>', methods=['POST','GET'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(title) > 60 or len(year) != 4:
            flash('Invalid input.')
            return redirect(url_for('edit',movie_id = movie_id))    #重填

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item update.')
        return redirect(url_for('index'))
    return render_template('edit.html',movie=movie)

@app.route('/movie/delete/<int:movie_id>', methods= ['POST'])      #TODO
@login_required
def delete(movie_id):
    movie_id = Movie.query.get_or_404(movie_id)
    db.session.delete(movie_id)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))

@app.route('/settings',methods=['POST','GET'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) >20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        current_user.name = name
        db.session.commit()
        flash('Settings update')
        return redirect(url_for('index'))
    return render_template('settings.html')


