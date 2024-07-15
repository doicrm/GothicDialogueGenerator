import argparse
from src.parser import InkParser
from src.file_saver import FileSaver
from customtkinter import *
import tkinter.filedialog as filedialog


class App(CTk):
    def __init__(self):
        super().__init__()
        self.file_path = ''

        self.geometry("400x300")

        self.choose_file_button = CTkButton(self, text="Open file", command=self.open_file)
        self.file_path_label = CTkLabel(self, text="No file selected")
        self.entry = CTkEntry(self, placeholder_text="Enter NPC name", width=250)
        self.generate_button = CTkButton(self, text="Generate dialogue", command=self.generate_dialogue)

        self.entry.pack(anchor="s", expand=True, pady=10)
        self.choose_file_button.pack(anchor="s", expand=True, pady=10)
        self.file_path_label.pack(pady=20)
        self.generate_button.pack(anchor="n", expand=True)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("Ink Files", "*.ink")]
        )
        if file_path:
            self.file_path_label.configure(text=file_path)
            self.file_path = file_path

    def generate_dialogue(self):
        if not self.file_path:
            print("No file selected")
            return

        npc_name = self.entry.get()
        if not npc_name:
            print("NPC name cannot be empty")
            return

        parsed_text = InkParser(self.file_path, npc_name).get_parsed_text()
        file_path = f"DIA_{npc_name}.d"
        FileSaver(file_path, parsed_text)
        print(f"Dialogue saved to `{file_path}`.")


def run_gui():
    app = App()
    app.mainloop()


def run_cli(file_path, npc_name):
    if not file_path:
        print("File path is required for CLI mode")
        return

    if not npc_name:
        print("NPC name is required for CLI mode")
        return

    parsed_text = InkParser(file_path, npc_name).get_parsed_text()
    output_file_path = f"DIA_{npc_name}.d"
    FileSaver(output_file_path, parsed_text)
    print(f"Dialogue saved to `{output_file_path}`.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gothic Dialogue Generator")
    parser.add_argument('file', type=str, help="Path to the .ink file", nargs='?')
    parser.add_argument('npc', type=str, help="NPC name", nargs='?')

    args = parser.parse_args()

    if args.file and args.npc:
        run_cli(args.file, args.npc)
    else:
        run_gui()
