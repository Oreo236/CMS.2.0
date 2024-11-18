from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
association_table1 = db.Table(
    "association1",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
)
association_table2 = db.Table(
    "association2",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"))
)
# your classes here
class Course(db.Model):
    """
    Course Model
    """
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    code = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    assignments = db.relationship("Assignment", cascade = "delete")
    instructors = db.relationship("User", secondary = association_table1, back_populates = "instructors")
    students = db.relationship("User", secondary = association_table2, back_populates = "students")



    def __init__(self, **kwargs):
        """
        Initialize Course object/entry
        """
        self.code = kwargs.get("code", "")
        self.name = kwargs.get("name", "")
    
    def serialize(self):
        """
        Serialize a course object 
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments":[s.serialize() for s in self.assignments],
            "instructors":[c.simple_serialize() for c in self.instructors],
            "students": [c.simple_serialize() for c in self.students]
        }
    
    def sim_serialize(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name
        }
 
class Assignment(db.Model):
    """
    Assignment Model
    """
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String, nullable = False)
    due_date = db.Column(db.String, nullable = False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable = False)

    def __init__(self, **kwargs):
        """
        Initialize Course object/entry
        """
        self.title = kwargs.get("title", "")
        self.due_date = kwargs.get("due_date", "")
        self.course_id = kwargs.get("course_id")

    def serialize(self):
        """
        Serialize a assignment object 
        """
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
            "course": Course.query.filter_by(id=self.course_id).first().sim_serialize()
        }
    
class User(db.Model):
    """
    User Model
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String, nullable = False)
    netid = db.Column(db.String, nullable = False)
    instructors = db.relationship("Course", secondary = association_table1, back_populates = "instructors")
    students = db.relationship("Course", secondary = association_table2, back_populates = "students")

    def __init__(self, **kwargs):
        """
        Initialize User object/entry
        """
        self.name = kwargs.get("name", "")
        self.netid = kwargs.get("netid", "")

    def serialize(self):
        """
        Serialize a user object 
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": [t.sim_serialize() for t in self.instructors] + [t.sim_serialize() for t in self.students]
        }
    def simple_serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid
        }


