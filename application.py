import os
import requests

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("beginning.html")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    print(request.method)
    if request.method == "GET":
        return render_template("registration_form.html")
    elif request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("password")
        if usernotexist(user) == True and password != "":
            inserting(user, password)
            return render_template("registration_success.html")
        else:
            return render_template("wronguser.html")


# inserting data into database
def inserting(user, password):
    db.execute("INSERT INTO readers (reader_name, reader_password) VALUES(:user,:password)",
               {"user": user, "password": password})
    db.commit()


# checking if user is not already in database
# Should return true when the user is not in the database
# should return false when the user is already in th e database
def usernotexist(user):
    rowCount = db.execute("SELECT * FROM readers WHERE reader_name = :user", {"user": user}).rowcount
    print("Row count found:", rowCount)
    if rowCount != 0:
        return False
    else:
        return True


@app.route("/login", methods=["POST", "GET"])
def log_in():
    if (request.method == "GET"):
        return render_template("login_form.html")
    elif (request.method == "POST"):
        user = request.form.get("user")
        password = request.form.get("password")
        reader_id = get_reader_id_from_user_and_password_if_they_match(user, password)
        session["reader_id"] = reader_id
        return render_template("home_page.html")


# checking if credentials match
def get_reader_id_from_user_and_password_if_they_match(user, password):
    user_id = db.execute("SELECT reader_id FROM readers WHERE reader_name= :user AND reader_password= :password",
                         {"user": user, "password": password}).fetchone()
    print("User Id: ", user_id)
    if user_id == None:
        raise ValueError("Wrong username or password.")
    else:
        return user_id


@app.route("/search", methods=["GET", "POST"])
def search():
    if (request.method == "GET"):
        return render_template("home_page.html")
    elif (request.method == "POST"):
        title = request.form.get("title")
        author = request.form.get("author")
        isbn = request.form.get("isbn")
        year = request.form.get("year")
        result = checkifitemindb(title, author, isbn, year)
        if result == "Unable to find query":
            return render_template("nosuchfile.html")
        else:
            print("Result: ", result)
            return render_template("home_page.html", result=result)


@app.route("/log_out")
def log_out():
    session.clear()
    return render_template("beginning.html")


# checking if user input is in database
def checkifitemindb(title, author, isbn, year):
    titlesAsTuples = db.execute("SELECT title FROM books").fetchall()
    authorsAsTuples = db.execute("SELECT author FROM books").fetchall()  # This is a list of tuples
    isbnsAsTuples = db.execute("SELECT isbn FROM books").fetchall()
    yearsAsTuples = db.execute("SELECT year FROM books").fetchall()
    authorsAsList = convert_list_from_tuple_to_string(authorsAsTuples)
    titlesAsList = convert_list_from_tuple_to_string(titlesAsTuples)
    isbnsAsList = convert_list_from_tuple_to_string(isbnsAsTuples)
    yearsAsList = convert_list_from_tuple_to_string(yearsAsTuples)

    for item in titlesAsList:
        if title in item and title != "":
            return db.execute("SELECT * FROM books WHERE title LIKE :item", {"item": item}).fetchall()
        else:
            title=title.capitalize()
            if title in item and title != "":
                return db.execute("SELECT * FROM books WHERE title LIKE :item", {"item": item}).fetchall()
    
    for item in authorsAsList:
        if author in item and author != "":
            return db.execute("SELECT * FROM books WHERE author LIKE :item", {"item": item}).fetchall()
        else: 
            author=author.capitalize()
            if author in item and author != "":
                return db.execute("SELECT * FROM books WHERE author LIKE :item", {"item": item}).fetchall()

    for item in isbnsAsList:
        if isbn == item and isbn != "":
            return db.execute("SELECT * FROM books WHERE isbn=:item", {"item": item}).fetchall()

    for item in yearsAsList:
        if year == item and year !="":
            return db.execute("SELECT * FROM books WHERE year=:item", {"item": item}).fetchall()

#    return render_template("nosuchfile.html")
    return "Unable to find query"


def convert_list_from_tuple_to_string(list_of_tuples):
    new_list = []
    for tupl in list_of_tuples:
        new_list.append(tupl[0])
    return new_list
def convertTuple(tup): 
    str =  ''.join(tup) 
    return str
    

@app.route("/search_det/<isbn>") #TODO : Check how will int react with database
def search_det(isbn):
    
    book = db.execute("SELECT * from books WHERE isbn =:isbn", {"isbn": isbn}).fetchone()
    print(f"Book ISBN: {book.isbn}, Title:  {book.title}, Author: {book.author}, Year of publishing: {book.year}.")
    reviews= db.execute("SELECT * from reviews WHERE isbn=:isbn", {"isbn": isbn}).fetchall()
    for review in reviews: 
        print(f" Reviews: {review.review_text}")
    reader_id= session["reader_id"][0]

    return render_template("bookdetails.html", book=book, reviews=reviews)

@app.route("/getIsbnReviewFromGoodReadsApi/<isbn>")
def getIsbnReviewFromGoodReadsApi(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "VlL3esMeQRAzGnVCtjeqQ", "isbns": isbn})
    data= res.json()
    average_rating= data["books"][0]["average_rating"]
    reviews_count= data["books"][0]["work_reviews_count"]

    return render_template("goodreadreview.html", average_rating=average_rating, reviews_count=reviews_count)

@app.route("/add_review/<isbn>", methods=["GET", "POST"])
def add_review(isbn):
    reader_id= int(session["reader_id"][0])
    if (request.method == "GET"):
        return render_template("addedreview.html", isbn=isbn)
    elif (request.method == "POST"):
        stars= request.form.get("stars")
        review_text= request.form.get("your_review")
        if if_user_already_added_review(reader_id, isbn)==True:
            return render_template("alreadyaddedreview.html")
        elif if_user_already_added_review(reader_id, isbn)==False:
            db.execute("INSERT INTO reviews (review_text, stars, reader_id, isbn) VALUES(:review_text,:stars,:reader_id,:isbn)", {"review_text":review_text, "stars":stars, "reader_id":reader_id, "isbn":isbn}) 
            db.commit()
            return "successfully added review"

def if_user_already_added_review(reader_id, isbn):
    review=db.execute("SELECT review_text FROM reviews WHERE reader_id=:reader_id AND isbn=:isbn", {"reader_id":reader_id, "isbn":isbn}).fetchone()
    print("this is review", review)
    if review != None:
        return True
    else:
        return False

@app.route("/api/<isbn>")
def isbn_api(isbn):

    allisbn= db.execute("SELECT isbn FROM books").fetchall()
    listallisbn= convert_list_from_tuple_to_string(allisbn)
    if isbn not in listallisbn:
        return jsonify({"error": "Invalid isbn"}), 422

    books= db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchall()
    books= convert_list_from_tuple_to_string(books)
    average_rating= db.execute("SELECT AVG(stars) FROM reviews WHERE isbn=:isbn",{"isbn":isbn}).fetchall()
    average_rating= convert_list_from_tuple_to_string(average_rating)
    average_rating= str(average_rating[0])
    reviews_count= db.execute("SELECT review_text, COUNT(*) FROM reviews WHERE isbn=:isbn GROUP BY review_text",{"isbn":isbn}).fetchall()
    reviews_count= convert_list_from_tuple_to_string(reviews_count)
    title= db.execute("SELECT title FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchall()
    title= convert_list_from_tuple_to_string(title)
    author= db.execute("SELECT author FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchall()
    author= convert_list_from_tuple_to_string(author)
    year= db.execute("SELECT year FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchall()
    year= convert_list_from_tuple_to_string(year)
    return jsonify({
            "isbn": isbn,
            "title": title[0],
            "author": author[0],
            "year": year[0],
            "average_rating":average_rating,
            "reviews_count":reviews_count

        })