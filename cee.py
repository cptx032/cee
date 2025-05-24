import glob
import cee_core
from plugins import random_ext, func_ext
from typing import Type


def get_all_cee_files() -> list[str]:
    return glob.glob("./*.cee")


plugins: list[Type] = [random_ext.RandomKeywordPlugin, func_ext.FuncPlugin]

if __name__ == "__main__":
    source = """

@func main() int {
    printf("hey");
    return 0;
}

"""
    for plugin in plugins:
        while command := cee_core.get_cee_command(source, plugin.name):
            if not plugin.is_command_valid(command):
                print("Invalid Command")
                break

            changes_to_do: cee_core.SourceCodeChanges = plugin.get_proposed_changes(
                command
            )
            if not changes_to_do.is_valid():
                print("Invalid Changes")
                break

            if changes_to_do.replacement_text:
                source = cee_core.replace_source(
                    source,
                    command.start_pos,
                    command.end_pos,
                    changes_to_do.replacement_text,
                )
    print(source)

"""
@import arena.cee
// what this does is: is replaces by #include "./.cee/arena.c"

@func main(int argc) int {
    return 0;
}
// just revert the order

@func (int argc) int {
    return 0;
}
// so we can use as:
register_handler(@func {
    printf("%s\n", "Hey!");
});

// it is the same as the function, but without name

struct myStruct
{
    int @random {my_pointer};
};
// when transpiled, it will become:
struct myStruct
{
    int xouh87hfu;
};

@test {
    @assert 1 == 1
}

"""
