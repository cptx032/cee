#!/usr/bin/env python3
import shutil
import sys
import cee_utils
import os


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
    clear_cee_folder()
    cmd_arguments = map(process_cee_file_from_cmd, sys.argv[1:])
    command_to_run = " ".join(cmd_arguments)
    print(f"Running {command_to_run}")
    os.system(command_to_run)

"""
@import arena.cee
// what this does is: is replaces by #include "./.cee/arena.c"

@func (int argc) int {
    return 0;
}
// we can use as:
register_handler(@func {
    printf("%s\n", "Hey!");
});

// it is the same as the function, but without name

@test {
    @assert 1 == 1
}

"""
