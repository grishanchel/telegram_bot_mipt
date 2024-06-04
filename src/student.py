class Student:
    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.courses = []

    def enroll_course(self, course):
        self.courses.append(course)

    def drop_course(self, course):
        self.courses.remove(course)
