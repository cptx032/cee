import cee_core
import parser_utils
from plugins import func_plugin
import plugins_core


class Plugin(plugins_core.BasePlugin):
    names: list[str] = ["defer"]
    description: str = (
        "Responsible for guarantee that a function will be called before the "
        "end of context"
    )

    def is_command_valid(self) -> bool:
        if not self.command.arguments.strip():
            return False
        return True

    def get_ignore_regions(self) -> list[tuple[int, int]]:
        ignore_regions: list[tuple[int, int]] = []
        for name in func_plugin.Plugin.names:
            cee_command: str = f"@{name}"
            function_instances: list[int] = parser_utils.find_substring_indexes(
                self.command.body, cee_command
            )
            for instance_index in function_instances:
                after_cee_command_index: int = instance_index + len(cee_command)
                brackets_start: int = self.command.body.find(
                    "{", after_cee_command_index
                )
                if brackets_start == -1:
                    raise ValueError("It was not possible to parse inner function")
                brackets_end: int | None = parser_utils.find_closing_brackets(
                    self.command.body, brackets_start
                )
                if brackets_end is None:
                    raise ValueError("It was not possible to parse inner function")
                ignore_regions.append((brackets_start, brackets_end))
        return ignore_regions

    def get_valid_indexes(
        self, ignore_regions: list[tuple[int, int]], indexes: list[int]
    ) -> list[int]:
        final_indexes: list[int] = []
        for index in indexes:
            to_add: bool = True
            for start, end in ignore_regions:
                if index in range(start, end + 1):
                    to_add = False
                    break
            if to_add:
                final_indexes.append(index)
        return final_indexes

    def get_defer_command(self) -> str:
        command_to_include: str = self.command.arguments.strip()
        if not command_to_include.endswith(";"):
            command_to_include += ";"
        return command_to_include

    def is_last_line_a_return(self, source: str) -> bool:
        last_line: str = [i for i in source.split("\n") if i.strip()][-1]
        return "return" in last_line

    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        ignore_regions = self.get_ignore_regions()
        body_source: str = self.command.body[1:-1]
        command_to_include: str = self.get_defer_command()
        return_indexes = parser_utils.find_substring_indexes(body_source, "return")
        return_indexes = self.get_valid_indexes(ignore_regions, return_indexes)
        # when we insert a substring inside the string we change the indexes
        # of the return statements that we found before, this is why we iterate
        # over the return indexes in the inverse order, because while inserting
        # in the end of the source the indexes of the beginning remains
        # unchanged
        for index in return_indexes[::-1]:
            body_source = parser_utils.insert_into_index(
                source=body_source,
                value_to_insert="\n" + command_to_include + "\n",
                index=index,
            )

        if not self.is_last_line_a_return(body_source):
            body_source += "\n" + command_to_include

        return cee_core.SourceCodeChanges(replacement_text=body_source)
