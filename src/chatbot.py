class ChatBot:
    def __init__(self):
        self.students = []
        self.teachers = []

    def register_student(self, student):
        self.students.append(student)

    def register_teacher(self, teacher):
        self.teachers.append(teacher)

    def find_student_by_email(self, email):
        for student in self.students:
            if student.email == email:
                return student
        return None
