from datetime import datetime

from bson import Binary, ObjectId
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import os
import uuid

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your_secret_key'
client = MongoClient('mongodb://localhost:27017/')
db_t = client.teachers
db_s = client.student
db = client['blog_db']
posts_collection = db['posts']
favourite_table = db["mainfavourite"]
comments_collection = db['comments']
app.config['UPLOAD_FOLDER'] = 'static/images'
app.debug = True

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/student_registration', methods=['GET', "POST"])
def student_registration():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['pass']
        confirm_password = request.form['conf_pass']
        print(first_name)
        if password == confirm_password:
            student = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": password
            }
            print(student)
            db_s.student.insert_one(student)
            session['email'] = email
            session['password'] = password
            return redirect(url_for('dashboard'))
        else:
            return "Passwords do not match"
    return render_template('student_registration.html')
@app.route('/student_login', methods=['GET', "POST"])
def student_login():
    if request.method == "POST":
        username = request.form["uname"]
        password = request.form["psw"]
        remember = request.form.get("remember")
        if authenticate(username, password,db_s['student']):
            return redirect("/home")
            session['email'] = email
            session['password'] = password
        else:
            return render_template("student_login.html", error="Invalid login credentials.")

    return render_template("student_login.html")







@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('homepage'))
    else:
        return redirect(url_for('teacher_login'))


@app.route('/registration', methods=['GET', "POST"])
def teacher_registration():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        deg = request.form['deg']
        int = request.form['int']
        email = request.form['email']
        password = request.form['pass']
        confirm_password = request.form['conf_pass']
        print(first_name)
        if password == confirm_password:
            teacher = {
                "first_name": first_name,
                "last_name": last_name,
                "deg": deg,
                "int": int,
                "email": email,
                "password": password
            }
            print(teacher)
            db_t.teachers.insert_one(teacher)
            session['email'] = email
            session['password'] = password
            return redirect(url_for('homepage'))
        else:
            return "Passwords do not match"
    return render_template('teacher_registration.html')


@app.route('/login', methods=['GET', "POST"])
def teacher_login():
    if request.method == "POST":
        email = request.form["uname"]
        password = request.form["psw"]

        remember = request.form.get("remember")
        if authenticate(email, password,db_t['teachers']):
            session['email'] = email
            session['password'] = password
            return redirect("/homepage")
        else:
            return render_template("teacher_login.html", error="Invalid login credentials.")
    return render_template("teacher_login.html")



def authenticate(username, password,table):
    user = table.find_one({'email': username})
    if user:
        if user['password'] == password:
            return True
    return False



@app.route('/homepage')
def homepage():
    if "email" in session:
        user = session["email"]
    posts = list(posts_collection.find())
    return render_template('homepage.html', **locals())

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'email' in session:
        if request.method == 'POST':
            title = request.form['title']
            tags = request.form['tags'].split(',')
            description = request.form['description']
            referance = request.form['reference'].split('/n')
            time=datetime.now()
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post = {
                'date_time':time,
                'user':db_t['teachers'].find_one({'email':session['email']}),
                'title': title,
                'tags': tags,
                'description': description,
                'image_path': os.path.join(app.config['UPLOAD_FOLDER'], filename),
                'referance':referance
            }
            temp_post=posts_collection.insert_one(post)
            print(temp_post)
            return redirect(url_for('homepage'))
        else:
            return render_template('create_post.html')
    else:
        return 'You are not logged in'

@app.route('/fav/<string:id>', methods=['GET', "POST"])
def fav(id):
    if "email" in session:
        user = session["email"]
    data = posts_collection.find_one({"_id": ObjectId(id)})
    data["person"]= user

    if request.method=="POST":
        favourite_table.insert_one(data)
        return redirect("/")

@app.route('/favPage', methods=['GET', "POST"])
def favouritePage():
    if "email" in session:
        user = session["email"]
    list1 = {}
    posts = list(favourite_table.find({"person": user}))
    return render_template("favourite.html", **locals())

@app.route('/edit/<string:id>', methods=['GET', "POST"])
def edit (id):
    data = posts_collection.find_one({"_id": ObjectId(id)})
    print(data)
    if request.method == 'POST':
        posts_collection.delete_one({"_id": ObjectId(id)})
        title = request.form['title']
        tags = request.form['tags'].split(',')
        description = request.form['description']
        referance = request.form['reference'].split('/n')
        time=datetime.now()
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        post = {
            'date_time':time,
            'user':db_t['teachers'].find_one({'email':session['email']}),
            'title': title,
            'tags': tags,
            'description': description,
            'image_path': os.path.join(app.config['UPLOAD_FOLDER'], filename),
            'referance':referance
        }
        temp_post=posts_collection.insert_one(post)
        print(temp_post)
        return redirect(url_for('homepage'))
    return render_template("edit.html", **locals())

@app.route('/delete/<string:id>', methods=['GET', "POST"])
def delete (id):
    data = posts_collection.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        posts_collection.delete_one({"_id": ObjectId(id)})
        favourite_table.delete_one({"_id": ObjectId(id)})
        return redirect('/')
    return render_template("delete.html")


@app.route('/search')
def search():
    query = request.args.get('query')
    print(query)
    posts = list(posts_collection.find({'title':{'$regex':query, '$options':'i'}}))
    return render_template('search_result.html', posts=posts)

@app.route('/post/<post_id>')
def show_post(post_id):
    id=post_id
    post_id = ObjectId(post_id)
    post = posts_collection.find_one({'_id': post_id})

    print (post)
    comments = list(comments_collection.find({'post_id': id}))
    print(comments)
    return render_template('post.html', **locals())



@app.route('/filter/<string:tag>')
def filter(tag):
    print(tag)
    posts = list(posts_collection.find({'tags': tag}))
    print(posts)
    return render_template('filter_results.html', **locals())


@app.route('/post/<post_id>', methods=['POST'])
def add_comment(post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    comment = request.form.get('comment')
    comments_collection.insert_one({'post_id':post_id,'user': db_t['teachers'].find_one({'email':session['email']}), 'text': comment,'date':datetime.now()})
    #posts_collection.save(post)
    return redirect('/post/{}'.format(post_id))

@app.route('/profile')
def profile():
    user = db_t['teachers'].find_one({'email':session['email']})
    return render_template('user_information.html', user=user)

@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'email' in session:
        post_id = ObjectId(post_id)

        if request.method == 'POST':
            title = request.form['title']
            tags = request.form['tags'].split(',')
            description = request.form['description']
            referance = request.form['reference'].split('/n')

            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                posts_collection.update_one({'_id':post_id},{'$set':{'title':title,tags:'tags','description':description,'referance':referance}})

            return redirect(url_for('homepage'))
        else:
            post = posts_collection.find_one({'_id': post_id})
            return render_template('edit_post.html',post=post)
    else:
        return 'You are not logged in'

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/login')
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)

