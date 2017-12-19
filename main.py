from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B112'

###########################################################################

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True) #primary key for blog entries
    title = db.Column(db.String(250)) #will go into title area
    body = db.Column(db.String(2048)) #will go into body area
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

###########################################################################
# redirect from 'home page' to blog page
@app.route('/')
def index():
    return redirect('/blog')

###########################################################################
    # '''     @app.before_request
    # def require_login():
    #     allowed_routes = ['login', 'register']
    #     if request.endpoint not in allowed_routes and 'email' not in session:
    #         return redirect('/login')
    # '''
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

###########################################################################

    # FROM GET IT DONE And User Signup (mixed together)
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']
    #     verify = request.form['verify']

    #     # TODO - validate user's data
    #     #                 
# error messages for failed validation
#     error_empty = 'Empty... please supply requested information'
#     error_spaces = 'Sorry, no spaces allowed'
#     error_length = 'Please use more than 3 characters and less than 20'
#     error_no_match = "Does not match first entry or not between 3 and 20 characters"
#     error_symbols = 'Enter a valid email (one "@", one ".", no spaces)'

#         # user_name validation
#     username = request.form['username']
#     empty_error_user_name = ''
#     if username == '':
#         empty_error_user_name = error_empty
#     elif len(username) < 3 or len(username) > 20:
#         empty_error_user_name = error_length
#     elif ' ' in username:
#         empty_error_user_name = error_spaces

#         # password validation
#     password = request.form['password']
#     empty_error_password = ''

#     if password == '':
#         empty_error_password = error_empty
#         password = ''
#     elif len(password) < 3 or len(password) > 20:
#         empty_error_password = error_length
#         password = ''
#     elif ' ' in password:
#         empty_error_password = error_spaces
#         password = ''

#         # verify_password validation
#     verify_password = request.form['verify_password']
#     match_error = ''
#     empty_error_verify_password = ''

#     if password == '':
#         empty_error_verify_password = error_empty
#         password == ''
#     elif verify_password != password:
#         match_error = error_no_match
#         password = ''

    # existing_user = User.query.filter_by(username=username).first()

    # if not existing_user:
    #     new_user = User(username, password)
    #     db.session.add(new_user)
    #     db.session.commit()
    #     session['username'] = username
    #     return redirect('/')
    # else:
    #     # TODO - user better response messaging
    #     return "<h1>Duplicate user</h1>"

    return render_template('signup.html')

#         # successful validation result
#     if empty_error_user_name == '' and empty_error_password == '' and match_error == '' and empty_error_verify_password == '' and email_error == '':
#         return render_template('welcome.html', username=username)

#         # failed validation result
#     else:
#         return render_template('index.html', empty_error_user_name=empty_error_user_name, 
#         empty_error_password=empty_error_password, match_error=match_error, 
#         empty_error_verify_password=empty_error_verify_password, username=username, password=password)

###########################################################################
# display all blogs

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blog_posts = Blog.query.all()
    blog_id = request.args.get('id')

    if blog_id:
        id = request.args.get('id')
        post_id = Blog.query.get(id)
        return render_template('/post.html',post_id=post_id)
    
    return render_template('/blog.html', blog_posts=blog_posts)

###########################################################################
# add new post

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    error_title = 'Please enter a title for your blog post'
    error_body = 'Please enter content for your blog post'
    error_empty_title = ''
    error_empty_body = ''

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