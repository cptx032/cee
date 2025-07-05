import cee_core
import plugins_core


class Plugin(plugins_core.BasePlugin):
    names: list[str] = ["test", "assert"]
    description: str = "Responsible for unit testing sources"

    def is_command_valid(self) -> bool:
        if not self.command.arguments.strip():
            return False
        return True

    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        return cee_core.SourceCodeChanges(replacement_text="// Hey")
