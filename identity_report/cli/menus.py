import inspect
import os
import sys

from ..managers.identity_results import IdentityResultManager
from ..test_files import test_files


def get_test_files():
    return test_files


def build_header():
    header = """
     _____    _            _   _ _          ______                      _   
    |_   _|  | |          | | (_) |         | ___ \                    | |  
      | |  __| | ___ _ __ | |_ _| |_ _   _  | |_/ /___ _ __   ___  _ __| |_ 
      | | / _` |/ _ \ '_ \| __| | __| | | | |    // _ \ '_ \ / _ \| '__| __|
     _| || (_| |  __/ | | | |_| | |_| |_| | | |\ \  __/ |_) | (_) | |  | |_ 
     \___/\__,_|\___|_| |_|\__|_|\__|\__, | \_| \_\___| .__/ \___/|_|   \__|
                                      __/ |           | |                   
                                     |___/            |_|                   
    ________________________________________________________________________
    
    AVAILABLE TEST FILES...
    ________________________________________________________________________
    """
    file_number = 1
    test_files_list = get_test_files()
    for test_file in test_files_list:
        header += '\n\t[{}] {}'.format(file_number, test_file)
        file_number += 1
    header += "\n    ________________________________________________________________________\n"
    return header


class PromptedValue(object):
    def __init__(self, prompt):
        super(PromptedValue, self).__init__()
        self.prompt = prompt

    def get_value(self):
        return str(input(self.prompt))


class Menu(object):
    def __init__(self, option_labels, option_values):
        super(Menu, self).__init__()
        self.banner = build_header()
        self.input = None
        self.option_labels = option_labels
        self.option_values = option_values

    def execute_choice(self, user_input):
        selected_option = self.option_values[(user_input - 1)]
        if not selected_option:
            selected = self.option_labels[(user_input - 1)]
            if selected:
                return ""
            return selected
        if inspect.isclass(selected_option) and issubclass(selected_option, Menu):
            menu = selected_option()
            user_input = menu.prompt()
            return menu.execute_choice(user_input)
        if isinstance(selected_option, list) or isinstance(selected_option, tuple):
            menu_or_callable = selected_option[0]
            args = selected_option[1:]
            new_args = []
            for arg in args:
                if isinstance(arg, PromptedValue):
                    new_args.append(arg.get_value())
                else:
                    new_args.append(arg)

            if inspect.isclass(menu_or_callable) and issubclass(menu_or_callable, Menu):
                menu = menu_or_callable(*new_args)
                user_input = menu.prompt()
                return menu.execute_choice(user_input)

            return menu_or_callable(*new_args)
        return selected_option()

    def get_full_prompt_text(self, output=None):
        prompt = [self.banner]
        if output:
            prompt.append("{}\n\n".format(output))
        option_num = 1
        for label in self.option_labels:
            prompt.append("{}: {}".format(option_num, label))
            option_num += 1
        prompt.append("\n")
        return "\n".join(prompt)

    def prompt(self, output=None):
        os.system("clear")
        valid_input = False
        while not valid_input:
            print(self.get_full_prompt_text(output))
            user_input = input("Enter the number of your choice: ")
            try:
                user_input = int(user_input)
            except:
                continue
            if (user_input - 1) in range(len(self.option_values)):
                valid_input = True
        return user_input


class MainMenu(Menu):
    def __init__(self):
        labels = [
            'Select result files for testing',
            'Exit'
        ]
        identity_result_manager = IdentityResultManager()
        options = [
            (identity_result_manager.extract_file_identity_results,
             PromptedValue("List files (comma separated by number associated in header above) to perform Identity Comparisons on: "),),
            sys.exit
        ]
        super(MainMenu, self).__init__(labels, options)
