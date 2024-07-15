import re
from src.file_reader import FileReader

class InkParser:
    def __init__(self, input_file, npc_name):
        self.ink_text = FileReader.read_file(input_file)
        self.npc_name = npc_name
        self.parsed_text = ""
        self.current_voice = ""
        self.parse_ink()

    def generate_exit_func(self):
        return f"""///////////////////////////////////////////////////////////////////////
//	Info EXIT
///////////////////////////////////////////////////////////////////////
instance DIA_{self.npc_name}_Exit (DIA_Exit_Default)
{{
\tnpc = {self.npc_name};
}};\n
"""

    def parse_ink(self):
        self.parsed_text += self.generate_exit_func()
        lines = self.ink_text.split('\n')
        state = 'START'
        dialogue_id = ''
        choice_id = ''
        dialogue_important = '0'
        dialogue_perm = '0'
        dialogue_desc = ""

        for line in lines:
            line = line.strip()

            if line.startswith('//'):
                self.parsed_text += f'\t{line}\n'

            if line.startswith('#'):
                if line.startswith('# IMPORTANT:'):
                    dialogue_important = self.extract_value(line)
                if line.startswith('# PERMANENT:'):
                    dialogue_perm = self.extract_value(line)
                if line.startswith('# DESC:'):
                    dialogue_desc = self.get_dialogue_description(line)

            if line.startswith('==='):
                if line.startswith('===='):
                    choice_id = self.extract_choice_id(line)
                    self.start_choice(choice_id)
                elif state == 'START':
                    dialogue_id = self.extract_id(line)
                    self.generate_dialogue(dialogue_id, dialogue_important, dialogue_perm, dialogue_desc)
                    state = 'DIALOGUE'
            
            if line.startswith('N:'):
                self.add_npc_line(line, dialogue_id, self.current_voice)

            if line.startswith('H:'):
                self.add_player_line(line, dialogue_id)

            if line.startswith('#'):
                if line.startswith('# VOICE:'):
                    self.current_voice = self.extract_value(line)
                elif line.startswith('# CLEAR_CHOICES'):
                    self.clear_choices(dialogue_id)

            if line.startswith('+'):
                self.add_choice(line, dialogue_id)

            if not line.strip(): # if line is empty
                self.end_dialogue()
                state = 'START'

            if line.startswith('->'):
                if line.startswith('-> DONE'):
                    self.exit_dialogue()
                    state = 'START'

    def extract_id(self, line):
        pattern = r'===\s*(.*?)\s*==='
        matches = re.findall(pattern, line)
        dialogue_id = ''.join(matches)
        return dialogue_id

    def extract_choice_id(self, line):
        pattern = r'====\s*(.*?)\s*===='
        matches = re.findall(pattern, line)
        choice_id = ''.join(matches)
        return choice_id

    def extract_value(self, line):
        return line.split(':')[-1].strip()
    
    def get_dialogue_description(self, line):
        return line.lstrip("# DESC:")

    def generate_dialogue(self, dialogue_id, dialogue_important, dialogue_perm, dialogue_desc):
        self.parsed_text += f"///////////////////////////////////////////////////////////////////////\n"
        self.parsed_text += f"//\tInfo {dialogue_id.upper()}\n"
        self.parsed_text += f"///////////////////////////////////////////////////////////////////////\n"
        self.parsed_text += f"instance DIA_{self.npc_name}_{dialogue_id} (C_INFO)\n"
        self.parsed_text += "{\n"
        self.parsed_text += f"\tnpc         = {self.npc_name};\n"
        self.parsed_text += f"\tnr          = 1;\n"
        self.parsed_text += f"\tcondition   = DIA_{self.npc_name}_{dialogue_id}_Condition;\n"
        self.parsed_text += f"\tinformation = DIA_{self.npc_name}_{dialogue_id}_Info;\n"

        if (dialogue_perm == 0):
            self.parsed_text += f"\tpermanent   = {str(bool(dialogue_perm)).upper()};\n"

        if (dialogue_important == 1 or dialogue_desc == ""):
            self.parsed_text += f"\timportant   = {str(bool(dialogue_important)).upper()};\n"

        if (dialogue_important == 0 or dialogue_desc != ""):
            self.parsed_text += f"\tdescription = \"{dialogue_desc}\";\n"

        self.parsed_text += "};\n\n"
        self.parsed_text += f"func int DIA_{self.npc_name}_{dialogue_id}_Condition()\n"
        self.parsed_text += "{\n"
        self.parsed_text += f"\treturn TRUE;\n"
        self.parsed_text += "};\n\n"
        self.parsed_text += f"func void DIA_{self.npc_name}_{dialogue_id}_Info()\n"
        self.parsed_text += "{\n"
        dialogue_perm = '0'
        dialogue_important = '0'
        dialogue_desc = ''

    def start_choice(self, choice_id):
        self.parsed_text += f"func void DIA_{self.npc_name}_{choice_id}()\n"
        self.parsed_text += "{\n"

    def end_dialogue(self):
        self.parsed_text += "};\n\n"

    def add_npc_line(self, line, dialogue_id, current_voice):
        npc_line = line.split('N:')[-1].strip()
        index = len(re.findall(fr'DIA_{self.npc_name}_{dialogue_id}_\w{{2}}_\d{{2}}"', self.parsed_text))
        self.parsed_text += f"\tAI_Output(self, other, \"DIA_{self.npc_name}_{dialogue_id}_{current_voice}_{str(index).zfill(2)}\"); //{npc_line}\n"

    def add_player_line(self, line, dialogue_id):
        player_line = line.split('H:')[-1].strip()
        index = len(re.findall(fr'DIA_{self.npc_name}_{dialogue_id}_\w{{2}}_\d{{2}}"', self.parsed_text))
        self.parsed_text += f"\tAI_Output(other, self, \"DIA_{self.npc_name}_{dialogue_id}_15_{str(index).zfill(2)}\"); //{player_line}\n"

    def add_choice(self, line, dialogue_id):
        pattern = r'\[(.*?)\]'
        matches = re.findall(pattern, line)
        dialogue_name = ''.join(matches)
        self.parsed_text += f"\tInfo_AddChoice(DIA_{self.npc_name}_{dialogue_id}, \"{dialogue_name}\", DIA_{self.npc_name}_{dialogue_id}_Choice{line[-2:]});\n"

    def exit_dialogue(self):
        self.parsed_text += "\tAI_StopProcessInfos(self);\n"

    def clear_choices(self, dialogue_id):
        self.parsed_text += f"\n\tInfo_ClearChoices(DIA_{self.npc_name}_{dialogue_id});\n"

    def get_parsed_text(self):
        return self.parsed_text
