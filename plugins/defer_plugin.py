import cee_core
from plugins import func_plugin


class Plugin:
    name: str | list[str] = [
        "defer",
    ]
    description: str = (
        "Responsible for guarantee that a function will be called before the "
        "end of context"
    )

    @staticmethod
    def is_command_valid(command: cee_core.CeeCommand) -> bool:
        if not command.arguments.strip():
            return False
        return True

    @staticmethod
    def get_proposed_changes(
        command: cee_core.CeeCommand,
    ) -> cee_core.SourceCodeChanges:
        for name in func_plugin.Plugin.name:
            if f"@{name}" in command.body:
                raise NotImplementedError("Inner functions aren't supported yet")
        final_source_lines: list[str] = []
        body_source: str = command.body[1:-1]
        lines: list[str] = [i for i in body_source.split("\n") if i.strip()]
        command_to_include: str = command.arguments.strip()
        if not command_to_include.endswith(";"):
            command_to_include += ";"
        return_in_last_line: bool = False

        # fixme > check if the command to include is already in the source code
        # so we can create a warning to avoid double free
        for i, line in enumerate(lines):
            last_line: bool = i == (len(lines) - 1)
            if "return" in line:
                if last_line:
                    return_in_last_line = True
                final_source_lines.append(command_to_include)
            final_source_lines.append(line)

        if not return_in_last_line:
            final_source_lines.append(command_to_include)

        return cee_core.SourceCodeChanges(
            replacement_text="\n".join(final_source_lines)
        )
