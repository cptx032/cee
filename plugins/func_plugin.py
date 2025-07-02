import cee_core
import cee_utils
import re
import plugins_core


class Plugin(plugins_core.BasePlugin):
    names: list[str] = [
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
    auto_comma: bool = True
    return_type_ignore_list: list[str] = ["->", ">", ":"]
    description: str = "Create functions in C using a modern syntax"

    def is_command_valid(self) -> bool:
        if not self.command.arguments.strip():
            return False
        return True

    @staticmethod
    def find_all_indexes(text: str, sub: str) -> list[int]:
        return [m.start() for m in re.finditer(re.escape(sub), text)]

    @staticmethod
    def random_word() -> str:
        return cee_utils.random_name(Plugin.lambda_length, Plugin.lambda_prefix)

    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        arguments: str = self.command.arguments.strip()
        open_indexes = Plugin.find_all_indexes(arguments, "(")
        close_indexes = Plugin.find_all_indexes(arguments, ")")
        # make possible not use parenthesys in case of void arguments
        # make possible to use Python style returns: ->
        # make possible to use Python style arguments type: name: Type
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

        for ignore_char in Plugin.return_type_ignore_list:
            return_type = return_type.replace(ignore_char, "")
        return_type = return_type.strip()

        # arguments without parenthesis
        function_arguments: str = arguments[
            open_indexes[0] + 1 : close_indexes[-1]
        ].strip()
        if not function_arguments:
            function_arguments = "void"

        argument_list: list[str] = [i.strip() for i in function_arguments.split(",")]
        for argument_index, argument in enumerate(argument_list):
            if ":" in argument:
                name, name_type = [i.strip() for i in argument.split(":")]
                argument_list[argument_index] = f"{name_type} {name}"

        function_arguments = ", ".join(argument_list)

        if Plugin.auto_comma:
            cee_utils.include_semicolon_in_body(self.command)

        function_source_code: str = (
            f"{return_type} {function_name}({function_arguments}) {self.command.body}"
        )

        if function_name:
            return cee_core.SourceCodeChanges(replacement_text=function_source_code)
        # handling the lambdas
        random_name: str = Plugin.random_word()
        return cee_core.SourceCodeChanges(
            replacement_text=random_name,
            new_functions=f"{return_type} {random_name}({function_arguments}) {self.command.body}",
        )
