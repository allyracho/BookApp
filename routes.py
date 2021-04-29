import os
import csv
from flask import render_template, redirect, flash, url_for, request
from bookapp import app, mydb, bcrypt
from bookapp.forms import LoginForm, RegistrationForm
from bookapp.models import User
from flask_login import login_user, current_user, login_required, logout_user
from datetime import datetime


# home screen
@app.route("/")
def home():
    results_list = []
    f = open("books.csv")
    reader = csv.reader(f)
    header = next(reader)
    if header != None:
        for data in reader:
            data_dict = dict()
            data_dict['Book_title'] = data[1]
            data_dict['Book_authors'] = data[2]
            data_dict['Book_ISBN'] = data[5]
            results_list.append(data_dict)
        posts = results_list
        return render_template("home.html", posts = posts)


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and bcrypt.check_password_hash(user.pwd_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful.', 'danger')
    return render_template('login.html', title='Login', form=form)


#register
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(login=form.login.data, password=hashed_password, name = form.name.data, address = form.address.data, phone_num = form.phone_num.data)
        mydb.session.add(user)
        mydb.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/user/<login>', methods=['GET', 'POST'])
def profile():
    form = LoginForm
    if request.method == 'GET':
        form.login.data = current_user.login
        form.name.data = current_user.name
    return render_template('profile.html', title = 'Account', form = form)


# search books & degree sep
@login_required
@app.route("/search_books", methods=["GET", "POST"])
def search_books():
    if request.method == "POST":
        book_query = request.form.get("search")
        book_query_like = '%' + book_query + '%'

        books = mydb.session.execute("SELECT * "
                           "FROM books "
                           "WHERE publisher LIKE :book_query_like OR title LIKE :book_query_like"
                           " OR author LIKE :book_query_like OR language LIKE:book_query_like"
                           " ORDER BY publish_date, avg_score",
        {"book_query_like": book_query_like}).fetchall()

        return render_template("search_books.html", no_books= (len(books) == 0), books=books)

# browse customer profile
@login_required
@app.route("/search_users", methods=['GET', 'POST'])
def search_users():
    if request.method == "POST":
        user_query = request.form.get("search")
        user_query_like = '%' + user_query + '%'

        profiles = mydb.session.execute("SELECT * FROM User WHERE login LIKE :user_query_like",
        {"user_query_like": user_query_like}).fetchall()

        return render_template("search_users.html", no_profiles= (len(profiles) == 0), profiles=profiles)

# book comments
@login_required
@app.route("/book_rating", methods=["GET", "POST"])
def book_rating():
    completed = False
    if request.method == 'POST':
        text = request.form.get('comment_text')
        rating = request.form.get('comment_rating')
        login = request.user.login
        date=datetime.date.now()
        sql = "INSERT INTO bookComments VALUES ('%s','%s','%s', '%s')"
        val = [(text,rating,login, date)]
        mydb.execute(sql, val)
        mydb.commit()

        completed = True

        if completed:
            flash('Your rating has been submitted!', 'success')
            return render_template("base.html")
    return render_template("book_rating.html")


# customer comments
@login_required
@app.route("/customer_rating", methods=["GET", "POST"])
def customer_rating():
    completed = False
    if request.method == 'POST':
        trust = request.form.get('comment_trust')
        rating = request.form.get('comment_rating')
        rated_user = request.form.get('rated_user')
        login = request.user.login
        date = datetime.date.now()

        if login != rated_user:
            sql = "INSERT INTO customerComments VALUES ('%s','%s', '%s', '%s', '%s')"
            val = [(trust,rating,rated_user,date,login)]
            mydb.execute(sql, val)
            mydb.commit()

        completed = True

        if completed:
            flash('Your rating has been submitted!', 'success')
            return render_template("base.html")
    return render_template("customer_rating")



'''
# book recommendation
@login_required
@app.route("/Recommended", methods=["GET", "POST"])
def book_rec():
    if request.method == 'POST':

'''

# place order
@app.route("/order", methods = ["GET","POST"])
@login_required
def order_book():
    completed = False
    orders = ""
    ISBN = ""
    if request.method == 'POST':
        ISBN = request.form.get('order_isbn')
        copies = request.form.get('order_copies')
        num_copies = int(copies)

        mydb.session.execute("SELECT copies FROM books WHERE ISBN = %s", ISBN)
        in_stock = (mydb.fetchone()[11])
        if in_stock>=num_copies:
            login = request.user.login
            time = datetime.date.now()
            price = (mydb.fetchone()[10])*num_copies

            sql = "INSERT INTO Orders (login,ISBN, total, copies, date) VALUES (%s,%s,%s,%s,%s)"
            val = (login, ISBN, price, num_copies, time)
            mydb.session.execute(sql, val)
            mydb.commit()

            sql ="UPDATE books SET in_stock = %s WHERE ISBN = %s"
            val = (in_stock-num_copies, ISBN)
            mydb.session.execute(sql, val)
            mydb.commit()

            completed = True

    if completed:
        flash('Your book has been ordered!', 'success')
        return render_template("base.html")
    return render_template("order.html")

@login_required
@app.route("/add_book", methods=['GET','POST'])
def add_Book():

    completed = False

    if request.method == 'POST':
        ISBN = request.form.get('ISBN')
        title = request.form.get('title')
        authors = request.form.get('authors')
        publisher = request.form.get('publisher')
        publication_date = request.form.get('publication_date')
        language_code = request.form.get('language_code')
        num_pages = request.form.get('num_pages')
        ratings_count = request.form.get('publisher')
        text_reviews_count = request.form.get('publication_date')
        average_rating = request.form.get('language_code')
        price = request.form.get('price')
        in_stock = request.form.get('copies')

        sql = "INSERT INTO Books VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s' ,'%s')"
        val = (ISBN,title,authors,publisher,publication_date,language_code,num_pages,
                ratings_count, text_reviews_count, average_rating,price,in_stock)
        mydb.session.execute(sql, val)
        mydb.commit()

        completed = True

        if completed:
            flash('The book has been added!', 'success')
            return render_template("base.html")
    return render_template("add_book.html")


# stock management
@app.route("/update_stock", methods=['GET','POST'])
@login_required
def update_stock():

    completed = False

    if request.method == 'POST':
        ISBN = request.form.get('update_stock_isbn')
        new_stock = request.form.get('stock')
        num_stock = int(new_stock)

        sql = "UPDATE Books SET stock_level = '%s' WHERE ISBN = '%s'"
        val = (num_stock, ISBN)
        mydb.session.execute(sql,val)
        mydb.commit()

        completed = True

        if completed:
            flash('Stock has been updated!', 'success')
            return render_template("base.html")
    return render_template("update_stock.html")



# review stats
@app.route("/book_stat", methods=['GET','POST'])
@login_required
def book_stat():
    if request.method == 'POST':
        ISBN = request.form.get('stat_isbn')
        limit = request.form.get('stat')
        limit = int(limit)

        sql = "SELECT ISBN FROM Orders where isbn = %s group by isbn, copies LIMIT = %s"
        val = (ISBN,limit)
        book_st = mydb.session.execute(sql,val).fetchall()

    return render_template("statistics.html", stats = book_st)

@app.route("/author_stat", methods=['GET','POST'])
@login_required
def author_stat():
    if request.method == 'POST':
        author = request.form.get('stat_author')
        limit = request.form.get('limit')
        limit = int(limit)

        sql = "SELECT b.author = %s FROM Orders o, Books b WHERE o.ISBN = b.ISBN ORDER BY sum(o.copies) LIMIT = %s"
        val = (author, limit)
        author_st = mydb.session.execute(sql,val).fetchall()

    return render_template("statistics.html", stats = author_st)


@app.route("/pub_stat", methods=['GET','POST'])
@login_required
def pub_stat():
    if request.method == 'POST':
        pub = request.form.get('stat_pub')
        limit = request.form.get('limit')
        limit = int(limit)

        sql = "SELECT b.publisher = %s FROM Orders o, Books b WHERE o.ISBN = b.ISBN ORDER BY sum(o.copies) LIMIT = %s"
        val = (pub, limit)
        pub_st = mydb.session.execute(sql, val).fetchall()

    return render_template("statistics.html", stats = pub_st)


@app.route("/trust_award", methods=['GET','POST'])
@login_required
def trusted_user():
    if request.method == "POST":
        limit = request.form.get('limit')
        limit = int(limit)
        score = mydb.session.execute("SELECT COUNT(type) FROM Award WHERE type ")

    return render_template("awards.html", score = score)


@app.route("/useful_award", methods=['GET','POST'])
@login_required
def useful_user():
    if request.method == "POST":
        limit = request.form.get('limit')
        limit = int(limit)
        score = mydb.session.execute("SELECT COUNT(type) FROM Award WHERE type ")

    return render_template("awards.html", score = score)
