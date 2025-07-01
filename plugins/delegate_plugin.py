import cee_core


class Plugin:
    name: str | list[str] = ["delegate"]
    description: str = "Alias for defining pointers to functions"

    @staticmethod
    def is_command_valid(command: cee_core.CeeCommand) -> bool:
        return True

    @staticmethod
    def get_proposed_changes(
        command: cee_core.CeeCommand,
    ) -> cee_core.SourceCodeChanges:
        delegate_name: str = command.arguments.strip()
        function_types: list[str] = [
            _type.strip() for _type in command.body.strip()[1:-1].split(",")
        ]
        if not function_types:
            function_types = ["void", "void"]
        return_type: str = function_types[0]
        arguments: list[str] = function_types[1:]
        arguments_str: str = ", ".join(arguments)
        return cee_core.SourceCodeChanges(
            replacement_text=f"{return_type} (*{delegate_name})({arguments_str})"
        )
