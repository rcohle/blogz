from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

###########################################################################

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True) #primary key for blog entries
    title = db.Column(db.String(250)) #will go into title area
    body = db.Column(db.String(2048)) #will go into body area

    def __init__(self, title, body):
        self.title = title
        self.body = body

###########################################################################
# redirect from 'home page' to blog page
@app.route('/')
def index():
    return redirect('/blog')

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
        new_post = Blog(title,body)
        db.session.add(new_post)
        db.session.commit()
        post_id = Blog.query.get(new_post.id)
        return redirect('/blog?id={0}'.format(new_post.id))
    else:
        return render_template('/newpost.html',error_empty_title=error_empty_title,error_empty_body=error_empty_body)

if __name__ == '__main__':
    app.run()