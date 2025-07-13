import enum
import dataclasses
from typing import Final


PLUGIN_CLASS_NAME: Final[str] = "Plugin"
CEE_STARTING_CHAR: Final[str] = "@"
CEE_FILE_EXTENSION: Final[str] = ".cee"


class StateMachineParser(enum.StrEnum):
    SEARCHING_ARGUMENTS = "searching_arguments"
    SEARCHING_ARGUMENTS_SUB_COMMAND = "searching_arguments_sub_command"
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
        return any(
            [
                self.replacement_text is not None,
                self.new_imports is not None,
                self.new_functions is not None,
            ]
        )


class IncludeState(enum.StrEnum):
    INSIDE_ONE_LINE_COMMENT = "inside_one_line_comment"
    INSIDE_MULTI_LINE_COMMENT = "inside_multi_line_comment"
    INSIDE_CEE_COMMAND = "inside_cee_command"
    INSIDE_MACRO = "include_macro"
    POSSIBLE_COMMENT = "possible_comment"
    SEARCHING = "searching"
