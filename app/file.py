import os


class File:
    def __init__(self, file_name):
        self.file_name = file_name
        if os.path.isfile(file_name):
            with open(file_name) as f:
                self.lines = list(filter(None, f.read().split('\n')))
        else:
            self.lines = []
        self.file = open(file_name, 'a')

    def contains(self, line):
        return line in self.lines

    def add_line(self, line):
        self.lines.append(line)
        self.file.write(line + '\n')

    def close(self):
        self.file.close()

    def contents(self):
        return self.lines
