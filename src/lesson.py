class Lesson:
    def __init__(self, title, content):
        self.title = title
        self.content = content

    def update_content(self, new_content):
        self.content = new_content
