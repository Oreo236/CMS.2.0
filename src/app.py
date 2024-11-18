import json
from db import db
from flask import Flask, request
from db import Course, Assignment, User
import os

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# your routes here
@app.route("/")
def was_here():
    return str(os.environ.get("NETID")) + " was here!"


@app.route("/api/courses/")
def get_courses():
    """
    Enpoint for getting all courses
    """
    return success_response({"courses" : [t.serialize() for t in Course.query.all()]})


@app.route("/api/courses/", methods = ["POST"])
def create_courses():
    """
    Enpoint for creating a new course
    """
    body = json.loads(request.data)
    codes = body.get("code", "")
    names = body.get("name", "")
    if codes ==  "":
        return failure_response("Invalid course code", 400)
    if names ==  "":
        return failure_response("Invalid course name", 400)
    new_course = Course(
        code = codes,
        name = names
    )
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(), 201)

@app.route("/api/courses/<int:course_id>/")
def get_course(course_id):
    """
    Endpoint for getting a course
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    return success_response(course.serialize())

@app.route("/api/courses/<int:course_id>/", methods = ["DELETE"] )
def delete_course(course_id):
    """
    Endpoint for deleting a specific course
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())

@app.route("/api/users/", methods = ["POST"])
def create_user():
    """
    Endpoint for creating a user
    """
    body = json.loads(request.data)
    name = body.get("name", None)
    netid = body.get("netid", None)
    if name is None:
        return failure_response("Invalid input: User's name not is provided", 400)
    if netid is None:
        return failure_response("Invalid input: User's netid not is provided", 400)
    new_user = User(
        name = name,
        netid = netid
    )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)

@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())

@app.route("/api/courses/<int:course_id>/add/", methods = ["POST"] )
def add_user_course(course_id):
    """
    Endpoint for adding a new user to a course
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    body = json.loads(request.data)
    user_id = body.get("user_id", None)
    type = body.get("type", None)
    if user_id is None:
        return failure_response("Invalid input: User_id is not provided", 400)
    if type is None:
        return failure_response("Invalid input: User's netid is not provided", 400)
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    if type == "instructor":
        course.instructors.append(user)
    else:
        course.students.append(user)
    db.session.commit()
    return success_response(course.serialize())



@app.route("/api/courses/<int:course_id>/assignment/", methods = ["POST"] )
def assignment_course(course_id):
    """
    Endpoint for creating a new assignment to a course
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found")
    body = json.loads(request.data)
    title = body.get("title", None)
    due_date = body.get("due_date", None)
    if title is None:
        return failure_response("Invalid input: assignment title not provided", 400)
    if due_date is None:
        return failure_response("Invalid input: assignment due date not provided", 400)
    new_assignment = Assignment(
        title = title,
        due_date = due_date,
        course_id = course_id
    )
    db.session.add(new_assignment)
    db.session.commit()
    return success_response(new_assignment.serialize(), 201)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)