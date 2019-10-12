import os

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import make_response
from flask import redirect
from flask import render_template
from datetime import datetime
from flask import request
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
import requests
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
    if("username" not in session):
        return redirect( url_for("signup") )
    return redirect( url_for("homepage") )

@app.route("/homepage")
def homepage():
    if("username" not in session):
        return redirect( url_for("signup") )
    return render_template("main.html", username=session["username"], id=session["id"], me=session["username"])

@app.route("/signup",methods=["POST", "GET"])
def signup():
    if("username" in session):
        return render_template("main.html", errormsg="already logged in", username=session["username"], id=session["id"], me=session["username"])
    if(request.method=="GET"):
        return render_template("signup.html")
    elif(request.method=="POST"):
        username=request.form["username"]
        password=request.form["password"]
        email=request.form["email"]
        if(username=="" or password=="" or email==""):
            return render_template("signup.html", errormsg="All fields above cannot be empty")
        elif(db.execute("SELECT * FROM users WHERE username = :username", {"username" : username}).rowcount > 0):
            return render_template("signup.html", unique="false")
        else:
            db.execute("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)", {"username" : username, "password" : password, "email" : email})
            session["username"]=username
            session["password"]=password
            session["email"]=email
            session["rating"]=0
            session["id"]=db.execute("SELECT id FROM users WHERE username = :username", {"username" : username}).fetchall()[0][0]
            db.commit()
            return redirect( url_for("homepage") )

@app.route("/login", methods=["POST", "GET"])
def login():
    if("username" in session):
        return render_template("main.html", errormsg="already logged in", username=session["username"], id=session["id"], me=session["username"])
    if(request.method=="GET"):
        return render_template("login.html")
    elif(request.method=="POST"):
        username=request.form.get("username")
        password=request.form.get("password")
        if(db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username" : username, "password" : password}).rowcount == 1):
            session["username"]=username
            session["password"]=password
            session["email"]=db.execute("SELECT email FROM users WHERE username = :username", {"username" : username}).fetchall()[0][0]
            session["rating"]=db.execute("SELECT rating FROM users WHERE username = :username", {"username" : username}).fetchall()[0][0]
            session["id"]=db.execute("SELECT id FROM users WHERE username = :username", {"username" : username}).fetchall()[0][0]
            db.commit()
            return redirect( url_for("homepage") )
        else:
            return render_template("login.html", errormsg="Wrong credentials!, pls try again")
@app.route("/logout", methods=["POST","GET"])
def logout():
    if("username" in session):
        session.pop("username", None)
        session.pop("password", None)
        session.pop("email", None)
        session.pop("rating", None)
        session.pop("id", None)
        return render_template("login.html", errormsg="Successfully logged out")
    else:
        return render_template("signup.html", errormsg="U actually haven't even logged in...")

@app.route("/forum", methods=["POST","GET"])
def forum():
    if("username" not in session):
        return redirect( url_for("login") )
    if(request.method=="GET"):
        return render_template("form.html", me=session["username"])
    elif(request.method=="POST"):
        if("rating" in request.form):
            all=db.execute("SELECT * FROM blogs").fetchall()
            all.sort(key=lambda blog: -blog.rating)
            return render_template("form.html", blogs=all, noresult=(len(all)==0), me=session["username"])
        if("recent" in request.form):
            all=db.execute("SELECT * FROM blogs").fetchall()
            all.reverse()
            return render_template("form.html", blogs=all, noresult=(len(all)==0), me=session["username"])
        tags=request.form.get("tags")
        tosearch=request.form.get("tosearch")
        temp=match(tosearch, tags) # temporary variable
        nores=0
        if(len(temp) == 0):
            nores=1
        return render_template("form.html", blogs=temp, noresult=nores, me=session["username"])

def match(tosearch, tags):
    allblogs=db.execute("SELECT * FROM blogs")
    res = []
    for blog in allblogs:
        if(tosearch != "" and tags != "" and ((tosearch.lower() in blog.title.lower()) or (tags.lower() == blog.animal.lower())) ):
            res.append(blog)
        elif(tosearch == "" and tags != "" and tags.lower() == blog.animal.lower()):
            res.append(blog)
        elif(tosearch != "" and tags == "" and tosearch.lower() in blog.title().lower()):
            res.append(blog)
        elif(tosearch == "" and tags == ""):
            res.append(blog)
    return res

@app.route("/blog/<string:name>", methods=["POST","GET"])
def blog(name): # all blogs of that user
    if("username" not in session):
        return redirect( url_for("login") )
    thisblog=db.execute("SELECT * FROM blogs WHERE username=:username", {"username":name}).fetchall() #blogs have unique id
    if(len(thisblog)==0):
        return render_template("blog.html", doesntexist=1, me=session["username"])
    return render_template("blog.html", blog=thisblog, me=session["username"])

@app.route("/create", methods=["POST","GET"])
def create():
    if("username" not in session):
        return redirect( url_for("login") )
    if(request.method=="GET"):
        return render_template("create.html", me=session["username"])
    elif(request.method=="POST"):
        content=request.form.get("content")
        animal=request.form.get("animal")
        title=request.form.get("title")
        if(db.execute("SELECT * FROM blogs WHERE username=:username AND animal=:animal AND content=:content AND title=:title", {"username":session["username"],"animal":animal,"content":content,"title":title}).rowcount > 0):
            return render_template("create.html", errormsg="U have posted about the exact same blog before", me=session["username"])
        db.execute("INSERT INTO blogs (animal, content, username, title) VALUES (:animal, :content, :username, :title)", {"animal":animal, "content":content, "username":session["username"], "title":title})
        db.commit()
        blogid=str(db.execute("SELECT id FROM blogs WHERE username=:username AND animal=:animal AND content=:content AND title=:title", {"username":session["username"],"animal":animal,"content":content,"title":title}).fetchall()[0][0])
        return redirect( url_for("blogpage", blogid=blogid) )

@app.route("/blogpage/<string:blogid>", methods=["POST","GET"])
def blogpage(blogid):
    if("username" not in session):
        return redirect( url_for("login") )
    if(db.execute("SELECT * FROM blogs WHERE id=:blogid", {"blogid":int(blogid)}).rowcount == 0):
        return render_template("blogpage.html", errormsg="blog requested does not exists", me=session["username"])
    username=db.execute("SELECT username FROM blogs WHERE id=:blogid", {"blogid":int(blogid)}).fetchall()[0][0]
    content=db.execute("SELECT content FROM blogs WHERE id=:blogid", {"blogid":int(blogid)}).fetchall()[0][0]
    title=db.execute("SELECT title FROM blogs WHERE id=:blogid", {"blogid":int(blogid)}).fetchall()[0][0]
    rating=db.execute("SELECT rating FROM blogs WHERE id=:blogid", {"blogid":int(blogid)}).fetchall()[0][0]
    return render_template("blogpage.html", username=username, content=content, title=title, rating=rating, me=session["username"])
@app.route("/profile/<string:username>", methods=["POST","GET"])
def profile(username):
    if("username" not in session):
        return redirect( url_for("login") )
    email=db.execute("SELECT email FROM users WHERE username=:username", {"username":username}).fetchall()[0][0]
    num=len(db.execute("SELECT * FROM blogs WHERE username=:username", {"username":username}).fetchall())
    return render_template("profile.html", username=username, email=email, num=num, me=session["username"])
