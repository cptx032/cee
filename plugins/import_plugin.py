import cee_core


class Plugin:
    name: str = "import"

    @staticmethod
    def is_command_valid(command: cee_core.CeeCommand) -> bool:
        if command.arguments.strip() != "":
            return False
        return True

    @staticmethod
    def get_proposed_changes(
        command: cee_core.CeeCommand,
    ) -> cee_core.SourceCodeChanges:
        name: str = command.body.strip()[1:-1].strip()
        endswith_h: bool = name.endswith(".h")
        endswith_c: bool = name.endswith(".c")
        endswith_cee: bool = name.endswith(cee_core.CEE_FILE_EXTENSION)

        replacement_text: str = ""
        if endswith_c or endswith_h:
            replacement_text = f"#include <{name}>"
        elif endswith_cee:
            new_path: str = cee_core.transpile_cee_source(name)
            replacement_text = f'#include "{new_path}"'
        else:
            replacement_text = f"#include <{name}.h>"

        return cee_core.SourceCodeChanges(replacement_text=replacement_text)
