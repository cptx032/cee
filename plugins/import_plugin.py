import cee_core
import cee_utils
import plugins_core


class Plugin(plugins_core.BasePlugin):
    names: list[str] = [
        "import",
        "use",
        "load",
        "require",
        "include",
        "using",
        "uses",
    ]
    description: str = (
        "Alias for #include .c/.h sources and the main transpiler for .cee sources"
    )

    def is_command_valid(self) -> bool:
        if self.command.arguments.strip() != "":
            return False
        return True

    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        libs: list[str] = [
            lib.strip() for lib in self.command.body.strip()[1:-1].strip().split(",")
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
