from flask import render_template, request, url_for, redirect, flash ,Response
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import and_,or_

from Another_eye import app, db
from Another_eye.models import User, Movie

import cv2

from Another_eye import socketio




@app.route('/' , methods=['GET','POST'])
def index():
    video_feed_url = url_for('video_feed')
    return render_template('index.html',video_feed_url=video_feed_url)


# def gen_video_frames():
#     camera = cv2.VideoCapture(0)    #TODO
#     while True:
#         success,frames = camera.read()
#         #para : success 一帧是否成功读取 ，frames 所读取的图像数据。
#         if not success:
#             break
#         #格式转换
#         _,buffer = cv2.imencode('.jpg',frames)
#         yield buffer.tobytes()
#     camera.release()

#here
def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @socketio.on('connect')
# def on_connect():
#     print('Client connected.')
#     for frame in gen_video_frames():
#         socketio.emit('video_frame',frame,binary=True)


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


