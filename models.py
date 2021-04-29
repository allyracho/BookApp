from bookapp import mydb, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(login):
    return User.query.get(login)


class User(mydb.Model, UserMixin):

    login = mydb.Column(mydb.String(100), primary_key = True, nullable=False)
    pwd_hash = mydb.Column(mydb.String(100), nullable = False)
    name = mydb.Column(mydb.String(100), nullable=False)
    address = mydb.Column(mydb.String(250))
    phone_num = mydb.Column(mydb.String(10))
    is_active = mydb.Column(mydb.Boolean,default=False)
    orders = mydb.relationship('Orders', backref = 'purchaser', lazy = True)
    award = mydb.relationship('Award', backref = 'winner', lazy = True)
    book_comment = mydb.relationship('bookComments', backref = "commentor", lazy = True)
    customer_comment = mydb.relationship('customerComments', backref="commentor", lazy=True)


    def __repr__(self):
        return f"User('{self.login}', '{self.name})'"

    def get_login(self):
            return self.login

    def is_active(self):
            return self.is_active

    def activate_user(self):
            self.is_active = True



class Books(mydb.Model):
    ISBN = mydb.Column(mydb.String(13), primary_key=True, nullable=False)
    title = mydb.Column(mydb.TEXT, nullable=False)
    authors = mydb.Column(mydb.TEXT)
    publisher = mydb.Column(mydb.TEXT)
    publication_date = mydb.String(mydb.DateTime)
    language_code = mydb.Column(mydb.TEXT)
    num_pages = mydb.Column(mydb.INT)
    ratings_count = mydb.Column(mydb.INT)
    text_reviews_count = mydb.Column(mydb.INT)
    average_rating = mydb.Column(mydb.DECIMAL(3,2))
    price = mydb.Column(mydb.DECIMAL(7,2), nullable=False)
    in_stock = mydb.Column(mydb.INT)
    orders = mydb.relationship('Orders', backref= 'book_purchased', lazy= True)

    def __repr__(self):
        return f"Books('{self.ISBN}', '{self.title}', '{self.authors}', '{self.price}')"


class Orders(mydb.Model):
    transactionID = mydb.Column(mydb.INT, primary_key=True, autoincrement=True)
    total = mydb.Column(mydb.DECIMAL(7,2))
    copies = mydb.Column(mydb.INT)
    order_date = mydb.Column(mydb.DateTime)
    ISBN = mydb.Column(mydb.String(13), mydb.ForeignKey("books.ISBN"), nullable=False)
    login = mydb.Column(mydb.String(100), mydb.ForeignKey("user.login"), nullable=False)

    def __repr__(self):
        return f"Orders('{self.transactionID}', '{self.login}', '{self.ISBN}', '{self.total}', '{self.copies})'"


class Award(mydb.Model):
    awardID = mydb.Column(mydb.INT, autoincrement=True, primary_key=True)
    type = mydb.Column(mydb.String(1))
    login = mydb.Column(mydb.String(100), mydb.ForeignKey("user.login"), nullable=False)

    def __repr__(self):
        return f"Award('{self.awardID}', '{self.type}', '{self.login}')"


class bookComments(mydb.Model):
    book_commentID = mydb.Column(mydb.INT, autoincrement=True,primary_key=True)
    comment_date = mydb.Column(mydb.DateTime)
    login = mydb.Column(mydb.String(100), mydb.ForeignKey("user.login"), nullable=False)
    text = mydb.Column(mydb.TEXT)
    rating = mydb.Column(mydb.INT)

    def __repr__(self):
        return f"Book_Comments('{self.book_commentID}')"


class customerComments(mydb.Model):
    cust_commentID = mydb.Column(mydb.INT, autoincrement=True,primary_key=True)
    comment_date = mydb.Column(mydb.DateTime)
    login = mydb.Column(mydb.String(100), mydb.ForeignKey("user.login"), nullable=False)
    rated_user = mydb.Column(mydb.String(100))
    level_of_trust = mydb.Column(mydb.String(1))
    rating = mydb.Column(mydb.String(4))

    def __repr__(self):
        return f"Customer_Comments('{self.cust_commentID}')"
