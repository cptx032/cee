import glob
import os
import enum
import string
import dataclasses
import importlib
from typing import Type, Final


PLUGIN_CLASS_NAME: Final[str] = "Plugin"
CEE_STARTING_CHAR: Final[str] = "@"
CEE_FILE_EXTENSION: Final[str] = ".cee"


def get_cee_folder() -> str:
    current_directory: str = os.getcwd()
    return os.path.join(current_directory, ".cee_build")


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
        module_path = (
            py_file.replace(os.path.dirname(__file__), "")
            .replace("/", ".")
            .replace(".py", "")
        )
        if module_path.startswith("."):
            module_path = module_path[1:]
        module = importlib.import_module(module_path)
        if PLUGIN_CLASS_NAME in dir(module):
            modules.append(module.Plugin)
    return modules


def is_cee_keyword_valid(cee_keyword: str) -> bool:
    cee_keyword = cee_keyword.replace(CEE_STARTING_CHAR, "")
    for c in cee_keyword.lower():
        if c not in string.ascii_lowercase:
            return False
    return True


class StateMachineParser(enum.StrEnum):
    SEARCHING_ARGUMENTS = "searching_arguments"
    SOURCE_CODE_CREATION = "source_code_creation"


@dataclasses.dataclass
class CeeCommand:
    name: str
    arguments: str
    body: str
    start_pos: int
    end_pos: int


@dataclasses.dataclass
class SourceCodeChanges:
    replacement_text: str | None = None
    new_imports: str | None = None
    new_functions: str | None = None

    def is_valid(self) -> bool:
        return any([self.replacement_text, self.new_imports, self.new_functions])


def get_cee_command(
    source_code: str, cee_keywords: str | list[str]
) -> CeeCommand | None:
    if type(cee_keywords) is str:
        cee_keywords = [cee_keywords]

    cee_keyword: str | None = None
    index: int = -1
    for keyword in cee_keywords:
        if not is_cee_keyword_valid(keyword):
            raise ValueError("Invalid cee keyword")

        keyword = keyword.strip()
        if not keyword.startswith(CEE_STARTING_CHAR):
            keyword = f"{CEE_STARTING_CHAR}{keyword}"

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
    state: StateMachineParser = StateMachineParser.SEARCHING_ARGUMENTS
    curly_brace_level: int = 0
    inner_source_code: str = ""
    arguments: str = ""
    current_index = index + len(cee_keyword)

    for c in source_code[current_index:]:
        match state:
            case StateMachineParser.SEARCHING_ARGUMENTS:
                if c == "{":
                    state = StateMachineParser.SOURCE_CODE_CREATION
                    inner_source_code += "{"
                else:
                    arguments += c
            case StateMachineParser.SOURCE_CODE_CREATION:
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

    return CeeCommand(
        name=cee_keyword.strip(),
        arguments=arguments,
        body=inner_source_code,
        start_pos=index,
        end_pos=curly_brace_end,
    )


def replace_source(source: str, start: int, end: int, new_source: str) -> str:
    return source[:start] + new_source + source[end:]


def transpile_cee_source(input_file_path: str) -> str:
    new_file_name = os.path.join(
        get_cee_folder(), input_file_path.replace(CEE_FILE_EXTENSION, ".c")
    )
    if os.path.exists(new_file_name):
        return new_file_name

    with open(input_file_path) as source_c_file:
        source_content = source_c_file.read()

    for plugin in get_plugins():
        while command := get_cee_command(source_content, plugin.name):
            if not plugin.is_command_valid(command):
                print("Invalid Command")
                break

            changes_to_do: SourceCodeChanges = plugin.get_proposed_changes(command)
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
    print(f"Writing to: {new_file_name}")
    if os.path.dirname(new_file_name):
        os.makedirs(os.path.dirname(new_file_name), exist_ok=True)

    with open(new_file_name, "w") as new_source:
        new_source.write(source_content)
    return new_file_name
