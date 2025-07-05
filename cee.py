#!/usr/bin/env python3
import cee_modes
import shutil
import cee_utils
import os
import argparse


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def get_color_text(text: str, color: str):
    end: str = "\033[0m"
    return color + text + end


def show_help():
    for plugin_class in cee_utils.get_plugins():
        other_names: list[str] = []
        plugin_name: str = plugin_class.names[0]
        if len(plugin_class.names) > 1:
            other_names = plugin_class.names[1:]
        description = getattr(plugin_class, "description", "")
        header = get_color_text(plugin_name, Color.BOLD)
        if description:
            header += f" - {description}"
        print(header)
        if len(plugin_class.names) > 1:
            print(
                "    Can be used with the aliases: "
                f"{get_color_text(', '.join(other_names), Color.PURPLE)}"
            )
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="CEE - C Extended Expressions")
    parser.add_argument(
        "mode", choices=[e.value for e in cee_modes.ModeEnum], help="Mode of operation"
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to the build or test mode",
    )
    args = parser.parse_args()
    match args.mode:
        case cee_modes.ModeEnum.BUILD:
            clear_cee_folder()
            cmd_arguments = map(process_cee_file_from_cmd, args.args)
            command_to_run = " ".join(cmd_arguments)
            print(f"Running {command_to_run}")
            os.system(command_to_run)
        case cee_modes.ModeEnum.HELP:
            show_help()


def clear_cee_folder() -> None:
    cee_folder: str = cee_utils.get_cee_folder()
    if os.path.exists(cee_folder):
        shutil.rmtree(cee_folder)
    os.mkdir(cee_folder)


def process_cee_file_from_cmd(cmd: str) -> str:
    if not cmd.endswith(".cee"):
        return cmd

    print(f"Processing {cmd}")
    return cee_utils.transpile_cee_source(cmd)


if __name__ == "__main__":
    main()
