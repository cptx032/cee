import cee_core
import cee_utils


class Plugin:
    name: str | list[str] = [
        "import",
        "use",
        "load",
        "require",
        "include",
        "using",
        "uses",
    ]

    @staticmethod
    def is_command_valid(command: cee_core.CeeCommand) -> bool:
        if command.arguments.strip() != "":
            return False
        return True

    @staticmethod
    def get_proposed_changes(
        command: cee_core.CeeCommand,
    ) -> cee_core.SourceCodeChanges:
        libs: list[str] = [
            lib.strip() for lib in command.body.strip()[1:-1].strip().split(",")
        ]

        includes: list[str] = []
        for lib in libs:
            endswith_h: bool = lib.endswith(".h")
            endswith_c: bool = lib.endswith(".c")
            endswith_cee: bool = lib.endswith(cee_core.CEE_FILE_EXTENSION)

            replacement_text: str = ""
            if endswith_c or endswith_h:
                replacement_text = f"#include <{lib}>"
            elif endswith_cee:
                new_path: str = cee_utils.transpile_cee_source(lib)
                replacement_text = f'#include "{new_path}"'
            else:
                replacement_text = f"#include <{lib}.h>"
            includes.append(replacement_text)

        return cee_core.SourceCodeChanges(replacement_text="\n".join(includes))
