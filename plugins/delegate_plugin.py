import cee_core
import plugins_core


class Plugin(plugins_core.BasePlugin):
    names: list[str] = ["delegate"]
    description: str = "Alias for defining pointers to functions"

    def is_command_valid(self) -> bool:
        return True

    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        delegate_name: str = self.command.arguments.strip()
        function_types: list[str] = [
            _type.strip() for _type in self.command.body.strip()[1:-1].split(",")
        ]
        if not function_types:
            function_types = ["void", "void"]
        return_type: str = function_types[0]
        arguments: list[str] = function_types[1:]
        arguments_str: str = ", ".join(arguments)
        return cee_core.SourceCodeChanges(
            replacement_text=f"{return_type} (*{delegate_name})({arguments_str})"
        )
