import enum
import string
import dataclasses


def is_cee_keyword_valid(cee_keyword: str) -> bool:
    cee_keyword = cee_keyword.replace("@", "")
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


def get_cee_command(source_code: str, cee_keyword: str) -> CeeCommand | None:
    if not is_cee_keyword_valid(cee_keyword):
        raise ValueError("Invalid cee keyword")

    cee_keyword = cee_keyword.strip()
    if not cee_keyword.startswith("@"):
        cee_keyword = f"@{cee_keyword}"

    # the empty space in the end is to avoid names collision
    cee_keyword += " "

    index = source_code.find(cee_keyword)
    if index == -1:
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
