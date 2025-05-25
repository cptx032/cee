import string
import random
import cee_core


class Plugin:
    name: str | list[str] = ["random"]
    names: dict[str, str] = {}

    @staticmethod
    def random_word(length: int) -> str:
        letters = string.ascii_lowercase
        # fixme > check if the random name generated is inside the list
        return "".join(random.choice(letters) for i in range(length))

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
