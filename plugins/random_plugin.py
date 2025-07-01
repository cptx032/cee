import cee_core
import cee_utils


class Plugin:
    name: str | list[str] = ["random"]
    names: dict[str, str] = {}
    name_length: int = 5
    description: str = "Generate random characters"

    @staticmethod
    def random_word(length: int) -> str:
        return cee_utils.random_name(Plugin.name_length)

    @staticmethod
    def is_command_valid(command: cee_core.CeeCommand) -> bool:
        if command.arguments.strip() != "":
            return False
        return True

    @staticmethod
    def get_proposed_changes(
        command: cee_core.CeeCommand,
    ) -> cee_core.SourceCodeChanges:
        name: str = command.body.strip()
        if name not in Plugin.names:
            Plugin.names[name] = Plugin.random_word(5)
        return cee_core.SourceCodeChanges(replacement_text=Plugin.names[name])
