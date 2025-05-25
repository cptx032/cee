import string
import random
import cee_core
from typing import Final

MODULE_TEMPLATE: Final[str] = """
#ifndef {module_name}
#define {module_name}
{source_body}
#endif
""".strip()


class Plugin:
    name: str | list[str] = ["module", "package", "mod", "unit", "library", "lib"]
    name_length: int = 5
    names: list[str] = []

    @staticmethod
    def random_word() -> str:
        letters = string.ascii_uppercase
        return "".join(random.choice(letters) for i in range(Plugin.name_length))

    @staticmethod
    def is_command_valid(command: cee_core.CeeCommand) -> bool:
        return True

    @staticmethod
    def get_proposed_changes(
        command: cee_core.CeeCommand,
    ) -> cee_core.SourceCodeChanges:
        name: str = command.arguments.strip()
        if not name:
            name = Plugin.random_word()
        name = cee_core.normalize_name(name, prefix="__").upper()
        if name not in Plugin.names:
            Plugin.names.append(name)
        return cee_core.SourceCodeChanges(
            replacement_text=MODULE_TEMPLATE.format(
                module_name=name, source_body=command.body[1:-1]
            )
        )
