from course import Course

class Teacher:
    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.courses = []

    def create_course(self, course_name):
        course = Course(course_name, self)
        self.courses.append(course)
        return course

    def add_lesson(self, course, lesson):
        course.add_lesson(lesson)
