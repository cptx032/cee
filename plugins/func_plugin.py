import cee_core
import re
import random
import string


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
    prefix: str = ""
    lambda_prefix: str = "__lambda_"
    lambda_length: int = 5

    @staticmethod
    def is_command_valid(command: cee_core.CeeCommand) -> bool:
        if not command.arguments.strip():
            return False
        return True

    @staticmethod
    def find_all_indexes(text: str, sub: str) -> list[int]:
        return [m.start() for m in re.finditer(re.escape(sub), text)]

    @staticmethod
    def random_word() -> str:
        letters = string.ascii_lowercase
        # fixme > check if the random name generated is inside the list
        return "".join(random.choice(letters) for i in range(Plugin.lambda_length))

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

        function_name: str = Plugin.prefix + arguments[: open_indexes[0]].strip()
        return_type: str = arguments[close_indexes[-1] + 1 :].strip()
        if not return_type:
            return_type = "void"

        # arguments without parenthesis
        function_arguments: str = arguments[
            open_indexes[0] + 1 : close_indexes[-1]
        ].strip()
        if not function_arguments:
            function_arguments = "void"

        function_source_code: str = (
            f"{return_type} {function_name}({function_arguments}) {command.body}"
        )

        if function_name:
            return cee_core.SourceCodeChanges(replacement_text=function_source_code)
        # handling the lambdas
        random_name: str = Plugin.lambda_prefix + Plugin.random_word()
        return cee_core.SourceCodeChanges(
            replacement_text=random_name,
            new_functions=f"{return_type} {random_name}({function_arguments}) {command.body}",
        )
