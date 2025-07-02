import cee_core
import cee_utils
import plugins_core


class Plugin(plugins_core.BasePlugin):
    names: list[str] = ["random"]
    random_names: dict[str, str] = {}
    name_length: int = 5
    description: str = "Generate random characters"

    @staticmethod
    def random_word(length: int) -> str:
        return cee_utils.random_name(Plugin.name_length)

    def is_command_valid(self) -> bool:
        if self.command.arguments.strip() != "":
            return False
        return True

    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        name: str = self.command.body.strip()
        if name not in Plugin.random_names:
            Plugin.random_names[name] = Plugin.random_word(5)
        return cee_core.SourceCodeChanges(replacement_text=Plugin.random_names[name])
