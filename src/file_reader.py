
class FileReader:
    def read_file(input_file):
        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except Exception as e:
            print(f"FileReader: {e}")
            pass