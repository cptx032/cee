from pathlib import Path
import importlib.util
from plugins import import_plugin
import glob
import os
import string
import importlib
from typing import Type
import cee_core
import random


def get_cee_folder() -> str:
    current_directory: str = os.getcwd()
    return os.path.join(current_directory, ".cee_build")


random_names_created: list = []


def random_name(length: int, prefix: str = ""):
    letters = string.ascii_lowercase
    name = prefix + "".join(random.choice(letters) for i in range(length))
    if name in random_names_created:
        return random_name(length, prefix)
    random_names_created.append(name)
    return name


def normalize_name(name: str, replace_char: str = "_", prefix: str = "") -> str:
    final_name: str = ""
    for c in name:
        if c in string.ascii_letters:
            final_name += c
        elif c.isdigit():
            final_name += c
        else:
            final_name += replace_char
    return prefix + final_name


def get_plugins() -> list[Type]:
    py_files = glob.glob(os.path.join(os.path.dirname(__file__), "plugins", "*.py"))
    py_files += glob.glob(os.path.join(os.getcwd(), ".cee", "plugins", "*.py"))
    modules: list[Type] = []

    for py_file in py_files:
        module_path: Path = Path(py_file).resolve()
        module_name: str = os.path.basename(py_file).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if not spec:
            raise ValueError("It was not possible to obtain the module spec")
        module = importlib.util.module_from_spec(spec)
        if not spec.loader:
            raise ValueError("Loader not found")
        spec.loader.exec_module(module)
        if cee_core.PLUGIN_CLASS_NAME in dir(module):
            modules.append(getattr(module, cee_core.PLUGIN_CLASS_NAME))
    return modules


def is_cee_keyword_valid(cee_keyword: str) -> bool:
    cee_keyword = cee_keyword.replace(cee_core.CEE_STARTING_CHAR, "")
    for c in cee_keyword.lower():
        if c not in string.ascii_lowercase:
            return False
    return True


def get_position_after_import_block(source: str) -> int | None:
    # fixme > move the dataclasses to other place to avoid this ciclic import
    state: cee_core.IncludeState = cee_core.IncludeState.SEARCHING
    last_char: str | None = None
    blank_chars = " \t\n"
    inner_cee_command_level = 0
    cee_command = ""
    last_cee_command_pos = -1
    for pos, c in enumerate(source):
        if state == cee_core.IncludeState.SEARCHING:
            if c == "/":
                state = cee_core.IncludeState.POSSIBLE_COMMENT
            elif c == "#":
                state = cee_core.IncludeState.INSIDE_MACRO
            elif c == cee_core.CEE_STARTING_CHAR:
                state = cee_core.IncludeState.INSIDE_CEE_COMMAND
                last_cee_command_pos = pos
            elif c not in blank_chars:
                return pos - 1
        elif state == cee_core.IncludeState.POSSIBLE_COMMENT:
            if c == "/":
                state = cee_core.IncludeState.INSIDE_ONE_LINE_COMMENT
            elif c == "*":
                state = cee_core.IncludeState.INSIDE_MULTI_LINE_COMMENT
        elif state == cee_core.IncludeState.INSIDE_ONE_LINE_COMMENT:
            if c == "\n":
                state = cee_core.IncludeState.SEARCHING
        elif state == cee_core.IncludeState.INSIDE_MACRO:
            if c == "\n":
                # fixme > handle multiline macros
                state = cee_core.IncludeState.SEARCHING
        elif state == cee_core.IncludeState.INSIDE_MULTI_LINE_COMMENT:
            if c == "/" and last_char == "*":
                state = cee_core.IncludeState.SEARCHING
        elif state == cee_core.IncludeState.INSIDE_CEE_COMMAND:
            cee_command += c

            if c == cee_core.CEE_STARTING_CHAR:
                inner_cee_command_level += 1
            elif c == "}":
                if inner_cee_command_level >= 1:
                    inner_cee_command_level -= 1
                elif inner_cee_command_level == 0:
                    command_name = cee_command.split()[0].strip()
                    if command_name in import_plugin.Plugin.names:
                        state = cee_core.IncludeState.SEARCHING
                        last_cee_command_pos = -1
                        cee_command = ""
                    else:
                        return last_cee_command_pos
        last_char = c
    return None


def get_cee_command(
    source_code: str, cee_keywords: list[str]
) -> cee_core.CeeCommand | None:
    cee_keyword: str | None = None
    index: int = -1
    for keyword in cee_keywords:
        if not is_cee_keyword_valid(keyword):
            raise ValueError("Invalid cee keyword")

        keyword = keyword.strip()
        if not keyword.startswith(cee_core.CEE_STARTING_CHAR):
            keyword = f"{cee_core.CEE_STARTING_CHAR}{keyword}"

        # the empty space in the end is to avoid names collision
        keyword += " "

        index = source_code.find(keyword)
        if index == -1:
            continue
        else:
            cee_keyword = keyword
            break

    if cee_keyword is None:
        return None

    curly_brace_end: int | None = None
    state: cee_core.StateMachineParser = cee_core.StateMachineParser.SEARCHING_ARGUMENTS
    curly_brace_level: int = 0
    inner_source_code: str = ""
    arguments: str = ""
    current_index = index + len(cee_keyword)
    arguments_brackets_level: int = 0

    for c in source_code[current_index:]:
        match state:
            case cee_core.StateMachineParser.SEARCHING_ARGUMENTS:
                if c == "{":
                    state = cee_core.StateMachineParser.SOURCE_CODE_CREATION
                    inner_source_code += "{"
                elif c == cee_core.CEE_STARTING_CHAR:
                    arguments += cee_core.CEE_STARTING_CHAR
                    state = cee_core.StateMachineParser.SEARCHING_ARGUMENTS_SUB_COMMAND
                else:
                    arguments += c
            case cee_core.StateMachineParser.SEARCHING_ARGUMENTS_SUB_COMMAND:
                if c == "{":
                    arguments_brackets_level += 1
                    arguments += c
                elif c == "}":
                    arguments += c
                    if arguments_brackets_level >= 1:
                        arguments_brackets_level -= 1
                    if arguments_brackets_level == 0:
                        state = cee_core.StateMachineParser.SEARCHING_ARGUMENTS
                else:
                    arguments += c
            case cee_core.StateMachineParser.SOURCE_CODE_CREATION:
                if c == "{":
                    curly_brace_level += 1
                    inner_source_code += "{"
                elif c == "}" and curly_brace_level:
                    curly_brace_level -= 1
                    inner_source_code += "}"
                elif c == "}" and (not curly_brace_level):
                    curly_brace_end = current_index + 1
                    inner_source_code += "}"
                    break
                else:
                    inner_source_code += c
        current_index += 1
    if curly_brace_end is None:
        raise ValueError("Malformatted command")

    return cee_core.CeeCommand(
        name=cee_keyword.strip(),
        arguments=arguments,
        body=inner_source_code,
        start_pos=index,
        end_pos=curly_brace_end,
    )


def replace_source(source: str, start: int, end: int, new_source: str) -> str:
    return source[:start] + new_source + source[end:]


def include_new_function(source_content: str, new_functions: str) -> str:
    position: int = get_position_after_import_block(source_content) or 0
    return (
        source_content[:position]
        + "\n"
        + new_functions
        + "\n"
        + source_content[position:]
    )


def transpile_cee_source(input_file_path: str) -> str:
    new_file_name = os.path.join(
        get_cee_folder(), input_file_path.replace(cee_core.CEE_FILE_EXTENSION, ".c")
    )
    if os.path.exists(new_file_name):
        return new_file_name

    with open(input_file_path) as source_c_file:
        source_content = source_c_file.read()

    for plugin_class in get_plugins():
        while command := get_cee_command(source_content, plugin_class.names):
            plugin_instance = plugin_class(command)
            if not plugin_instance.is_command_valid():
                print("Invalid Command")
                break

            changes_to_do: cee_core.SourceCodeChanges = (
                plugin_instance.get_proposed_changes()
            )
            if not changes_to_do.is_valid():
                print("Invalid Changes")
                break

            if changes_to_do.replacement_text:
                source_content = replace_source(
                    source_content,
                    command.start_pos,
                    command.end_pos,
                    changes_to_do.replacement_text,
                )
            if changes_to_do.new_functions:
                source_content = include_new_function(
                    source_content, changes_to_do.new_functions
                )
    print(f"Writing to: {new_file_name}")
    if os.path.dirname(new_file_name):
        os.makedirs(os.path.dirname(new_file_name), exist_ok=True)

    with open(new_file_name, "w") as new_source:
        new_source.write(source_content)
    return new_file_name


def include_semicolon_in_body(command: cee_core.CeeCommand) -> None:
    # fixme > implement the Microsoft way of using curly-braces
    source_lines: list[str] = command.body.split("\n")
    final_source: list[str] = []
    for line in source_lines:
        # empty line
        if not line.strip():
            final_source.append(line)
        # commads that not end in this line
        elif line.strip()[-1] in ",{}=;":
            final_source.append(line)
        # comments
        elif line.strip().startswith("//"):
            # fixme > handle multiline comments
            final_source.append(line)
        # macros
        elif line.strip().startswith("#"):
            final_source.append(line)
        else:
            final_source.append(f"{line};")
    command.body = "\n".join(final_source)
