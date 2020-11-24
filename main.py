import random, uuid, hashlib
from flask import Flask, render_template, request, make_response, redirect, url_for
from models import User, db

app = Flask(__name__)
db.create_all()  # create (new) tables in the database


@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("indexes.html", user=user)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    # hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # create a secret number
    secret_number = random.randint(1, 50)

    # see if user already exists
    user = db.query(User).filter_by(email=email).first()

    if not user:
        # create a User object
        user = User(name=name, email=email, secret_number=secret_number, password=hashed_password)

        # save the user object into a database
        db.add(user)
        db.commit()

        # check if user password is incorrect
        if hashed_password != user.password:
            return "Wrong password. Please try again."
        elif hashed_password == user.password:
            # create random session token for this user
            session_token = str(uuid.uuid4())

        # save session token
            user.session_token = session_token
            db.add(user)
            db.commit()

        # save user's st into a cookie
            response = make_response(redirect(url_for("index")))
            response.set_cookie("session_token", session_token)

            return response

    # save user's email into a cookie
    response = make_response(redirect(url_for('index')))
    response.set_cookie("email", email)

    return response


@app.route("/result", methods=["POST"])
def result():
    global message
    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")

    # get user from the database based on her/his email address
    user = db.query(User).filter_by(session_token=session_token).first()

    if guess == user.secret_number:
        message = "Correct! The secret number is {0}".format(str(guess))

        # create a new random secret number
        new_secret = random.randint(1, 50)

        # update the user's secret number
        user.secret_number = new_secret

        # update the user object in a database
        db.add(user)
        db.commit()

    elif guess > user.secret_number:
        if guess > 51:
            message = "Try with number inside the given range."
        else:
            message = "Your guess is incorrect. Try with smaller number."
    elif guess < user.secret_number:
        if guess < 1:
            message = "Try with number inside the given range."
        else:
            message = "Your guess is incorrect. Try with bigger number."

    return render_template("result.html", message=message)


@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    # get user from db based on session_token
    user = db.query(User).filter_by(session_token=session_token).first()

    # if - else conds.
    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index"))


@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")

    # get user from the db based on his session_token
    user = db.query(User).filter_by(session_token=session_token).first()

    # check the token
    if request.method == "GET":
        if user:
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")
        old_password = request.form.get("old-password")
        new_password = request.form.get("new-password")

        if old_password and new_password:
            hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()

            # compare both passwords
            if hashed_old_password == user.password:
                user.password = hashed_new_password
            else:
                return "Old password not correct. Please type in correct password."

        # update user object
        user.name = name
        user.email = email

        db.add(user)
        db.commit()

        return redirect(url_for("profile"))


@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")

    # get user from db
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if request.method == "GET":
        if user:  # push user inside it
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        # mark the deleted file as True (bool-value); fake delete, user stays in database
        user.deleted = True
        db.add(user)
        db.commit()
        return redirect(url_for("index"))


@app.route("/users", methods=["GET"])
def all_users():
    users = db.query(User).all()
    return render_template("users.html", users=users)


# check the user; user id = variable param for defining which user to check
@app.route("/user/<user_id>")
def user_details(user_id):  # parameter from route to function
    user = db.query(User).get(int(user_id))
    return render_template("user_details.html", user=user)


if __name__ == '__main__':
    app.run(port=5060)  # if you use the port parameter, delete it before deploying to Heroku
