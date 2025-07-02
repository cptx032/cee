import cee_core
import cee_utils
from typing import Final
import plugins_core

MODULE_TEMPLATE: Final[str] = """
#ifndef {module_name}
#define {module_name}
{source_body}
#endif
""".strip()


class Plugin(plugins_core.BasePlugin):
    names: list[str] = [
        "module",
        "package",
        "mod",
        "unit",
        "library",
        "lib",
        "once",
    ]
    name_length: int = 5
    module_names: list[str] = []
    description: str = "An alias for the #pragma once directive"

    @staticmethod
    def random_word() -> str:
        return cee_utils.random_name(Plugin.name_length, "")

    def is_command_valid(self) -> bool:
        return True

    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        name: str = self.command.arguments.strip()
        if not name:
            name = Plugin.random_word()
        name = cee_utils.normalize_name(name, prefix="").upper()
        if name not in Plugin.module_names:
            Plugin.module_names.append(name)

        cee_utils.include_semicolon_in_body(self.command)
        return cee_core.SourceCodeChanges(
            replacement_text=MODULE_TEMPLATE.format(
                module_name=name, source_body=self.command.body[1:-1]
            )
        )
