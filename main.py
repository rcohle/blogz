from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B112'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    body = db.Column(db.String(2048))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','blog','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users = users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        error_empty = 'Empty... please supply requested information'
        error_spaces = 'Sorry, no spaces allowed'
        error_length = 'Please use more than 3 characters and less than 20'
        error_no_match = "Does not match first entry or not between 3 and 20 characters"
        error_symbols = 'Enter a valid email (one "@", one ".", no spaces)'

        empty_error_user_name = ''
        if username == '':
            empty_error_user_name = error_empty
        elif len(username) < 3 or len(username) > 20:
            empty_error_user_name = error_length
        elif ' ' in username:
            empty_error_user_name = error_spaces
      
        empty_error_password = ''
        if password == '':
            empty_error_password = error_empty
            password = ''
        elif len(password) < 3 or len(password) > 20:
            empty_error_password = error_length
            password = ''
        elif ' ' in password:
            empty_error_password = error_spaces
            password = ''

        match_error = ''
        empty_error_verify_password = ''
        if password == '':
            empty_error_verify_password = error_empty
            password == ''
        elif verify != password:
            match_error = error_no_match
            password = ''

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            existing_message = 'Duplicate user, please use login page'
            return render_template('signup.html',existing_message=existing_message)

        elif empty_error_user_name == '' and empty_error_password == '' and match_error == '' and empty_error_verify_password == '':
            if not existing_user and empty_error_user_name == '' and empty_error_password == '' and match_error == '' and empty_error_verify_password == '':
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("Logged in")
            return render_template('newpost.html', username=username)

        else:
            return render_template('signup.html', empty_error_user_name=empty_error_user_name, empty_error_password=empty_error_password, match_error=match_error, empty_error_verify_password=empty_error_verify_password, username=username, password=password)

    return render_template('signup.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if 'id' in request.args:
        id = request.args.get('id')
        blog = Blog.query.get(id)
        return render_template('post.html', blog=blog)

    elif 'user' in request.args:
        user_id = int(request.args.get('user'))
        owner = User.query.get(user_id)
        blog_posts = Blog.query.filter_by(owner=owner).all()
        return render_template('blog.html', blog_posts=blog_posts)

    else:
        blog_posts = Blog.query.all()
        return render_template('blog.html', blog_posts=blog_posts)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    error_title = 'Please enter a title for your blog post'
    error_body = 'Please enter content for your blog post'
    error_empty_title = ''
    error_empty_body = ''

    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title == '':
            error_empty_title = error_title
        if body == '':
            error_empty_body = error_body

    if request.method == 'POST' and error_empty_body == '' and error_empty_title == '':
        new_post = Blog(title,body,owner)
        db.session.add(new_post)
        db.session.commit()
        post_id = Blog.query.get(new_post.id)
        return redirect('/blog?id={0}'.format(new_post.id))
    
    else:
        return render_template('/newpost.html',error_empty_title=error_empty_title,error_empty_body=error_empty_body)

if __name__ == '__main__':
    app.run()