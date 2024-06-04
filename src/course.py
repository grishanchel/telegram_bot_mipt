class Course:
    def __init__(self, name, teacher):
        self.name = name
        self.teacher = teacher
        self.lessons = []

    def add_lesson(self, lesson):
        self.lessons.append(lesson)

    def remove_lesson(self, lesson):
        self.lessons.remove(lesson)
