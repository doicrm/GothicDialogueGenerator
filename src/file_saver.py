
class FileSaver:
    def __init__(self, path, content):
        self.file_path = path
        self.content = content
        self.save_file()

    def save_file(self):
        try:
            with open(self.file_path, 'w') as file:
                file.write(f'{self.content}\n')
            print(f"File '{self.file_path}' created and written to successfully.")
        except Exception as e:
            print(f"FileSaver: {e}")