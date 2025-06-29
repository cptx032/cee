#!/usr/bin/env python3
import shutil
import cee_utils
import os
import argparse
import enum


class ModeEnum(enum.StrEnum):
    BUILD = "build"
    TEST = "test"


def main() -> None:
    parser = argparse.ArgumentParser(description="CEE - C Extended Expressions")
    parser.add_argument(
        "mode", choices=[e.value for e in ModeEnum], help="Mode of operation"
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Arguments to pass to the build or test mode",
    )
    args = parser.parse_args()
    if args.mode == ModeEnum.BUILD:
        clear_cee_folder()
        cmd_arguments = map(process_cee_file_from_cmd, args.args)
        command_to_run = " ".join(cmd_arguments)
        print(f"Running {command_to_run}")
        os.system(command_to_run)


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
