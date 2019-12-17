#!/usr/bin/env python
import os

from ..cli.menus import MainMenu


def main():
    output = None
    while True:
        main_menu = MainMenu()
        user_input = main_menu.prompt(output)
        output = None
        output = main_menu.execute_choice(user_input)


if __name__ == '__main__':
    main()

