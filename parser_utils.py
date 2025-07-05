import enum
import cee_core
from plugins import import_plugin


def find_substring_indexes(source: str, substring: str) -> list[int]:
    indexes = []
    start = 0
    while True:
        index = source.find(substring, start)
        if index == -1:
            break
        indexes.append(index)
        start = index + len(substring)
    return indexes


def insert_into_index(*, source: str, value_to_insert: str, index: int) -> str:
    return source[:index] + value_to_insert + source[index:]


class ParserState(enum.StrEnum):
    SEARCHING = "searching"
    POSSIBLE_COMMENT = "POSSIBLE_COMMENT"
    INSIDE_MACRO = "INSIDE_MACRO"
    INSIDE_ONE_LINE_COMMENT = "INSIDE_ONE_LINE_COMMENT"
    INSIDE_MULTI_LINE_COMMENT = "INSIDE_MULTI_LINE_COMMENT"


# fixme > check if we can use this function in the main parser
def find_closing_brackets(source: str, start_brackets_position: int) -> int | None:
    state = ParserState.SEARCHING
    last_char: str | None = None
    brackets_level: int = 0

    for pos, c in enumerate(
        source[start_brackets_position + 1 :], start=start_brackets_position + 1
    ):
        match state:
            case ParserState.SEARCHING:
                if c == "/":
                    state = ParserState.POSSIBLE_COMMENT
                elif c == "#":
                    state = ParserState.INSIDE_MACRO
                elif c == "{":
                    brackets_level += 1
                elif c == "}":
                    if brackets_level > 0:
                        brackets_level -= 1
                    else:
                        return pos
            case ParserState.POSSIBLE_COMMENT:
                if c == "/":
                    state = ParserState.INSIDE_ONE_LINE_COMMENT
                elif c == "*":
                    state = ParserState.INSIDE_MULTI_LINE_COMMENT
                else:
                    state = ParserState.SEARCHING
            case ParserState.INSIDE_ONE_LINE_COMMENT:
                if c == "\n":
                    state = ParserState.SEARCHING
            case ParserState.INSIDE_MULTI_LINE_COMMENT:
                if c == "/" and last_char == "*":
                    state = ParserState.SEARCHING
            case ParserState.INSIDE_MACRO:
                if c == "\n":
                    # fixme > handle multiline macros
                    state = ParserState.SEARCHING
        last_char = c
    return None


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
            else:
                state = cee_core.IncludeState.SEARCHING
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
