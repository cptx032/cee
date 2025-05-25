import cee_core
import re


class Plugin:
    name: str | list[str] = [
        "func",
        "function",
        "fn",
        "def",
        "proc",
        "procedure",
        "routine",
        "sub",
    ]

    @staticmethod
    def is_command_valid(command: cee_core.CeeCommand) -> bool:
        if not command.arguments.strip():
            return False
        return True

    @staticmethod
    def find_all_indexes(text: str, sub: str) -> list[int]:
        return [m.start() for m in re.finditer(re.escape(sub), text)]

    @staticmethod
    def get_proposed_changes(
        command: cee_core.CeeCommand,
    ) -> cee_core.SourceCodeChanges:
        arguments: str = command.arguments.strip()
        open_indexes = Plugin.find_all_indexes(arguments, "(")
        close_indexes = Plugin.find_all_indexes(arguments, ")")
        if len(open_indexes) != len(close_indexes):
            raise ValueError("Some parenthesis not closed")
        if not open_indexes:
            raise ValueError("Missing parenthesis")
        if not close_indexes:
            raise ValueError("Missing parenthesis")

        function_name: str = arguments[: open_indexes[0]].strip()
        return_type: str = arguments[close_indexes[-1] + 1 :].strip()
        if not return_type:
            return_type = "void"

        # arguments without parenthesis
        function_arguments: str = arguments[
            open_indexes[0] + 1 : close_indexes[-1]
        ].strip()
        if not function_arguments:
            function_arguments = "void"

        return cee_core.SourceCodeChanges(
            replacement_text=f"{return_type} {function_name}({function_arguments}) {command.body}"
        )
