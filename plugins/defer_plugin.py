import re
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
            cee_command = f"@{name}"
            instance_indexes = parser_utils.find_substring_indexes(
                self.command.body, cee_command
            )

            for index in instance_indexes:
                start = self.command.body.find("{", index + len(cee_command))
                if start == -1:
                    raise ValueError("It was not possible to parse inner function")

                end = parser_utils.find_closing_brackets(self.command.body, start)
                if end is None:
                    raise ValueError("It was not possible to parse inner function")

                ignore_regions.append((start, end))

        return ignore_regions

    def get_valid_indexes(
        self, ignore_regions: list[tuple[int, int]], indexes: list[int]
    ) -> list[int]:
        return [
            index
            for index in indexes
            if not any(start <= index <= end for start, end in ignore_regions)
        ]

    def get_defer_command(self) -> str:
        command_to_include: str = self.command.arguments.strip()
        if not command_to_include.endswith(";"):
            command_to_include += ";"
        return command_to_include

    def is_last_line_a_return(self, source: str) -> bool:
        last_line: str = [i for i in source.split("\n") if i.strip()][-1]
        return "return" in last_line

    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        body_source = self.command.body[1:-1]
        command_to_include = self.get_defer_command()
        ignore_regions = self.get_ignore_regions()
        return_indexes = self.get_valid_indexes(
            ignore_regions, parser_utils.find_substring_indexes(body_source, "return")
        )

        command_vars = self._extract_command_variables(command_to_include)
        return_expr_map = self._map_return_expressions(body_source, return_indexes)
        warnings = self._detect_variable_collisions(return_expr_map, command_vars)

        # Apply insertions
        new_body = self._insert_commands(
            body_source, return_indexes, command_to_include
        )

        if not self.is_last_line_a_return(new_body):
            new_body += "\n" + command_to_include

        for warning in warnings:
            print(warning)

        return cee_core.SourceCodeChanges(replacement_text=new_body)

    def _extract_command_variables(self, command: str) -> list[str]:
        match = re.search(r"\((.*?)\)", command)
        if not match:
            return []
        raw_args = match.group(1)
        return [v.strip() for v in raw_args.split(",") if v.strip()]

    def _map_return_expressions(
        self, source: str, valid_indexes: list[int]
    ) -> dict[int, str]:
        expr_map = {}
        regex = re.compile(r"\breturn\s+(.*?)(?:;|\n|$)", re.DOTALL)
        for match in regex.finditer(source):
            start = match.start()
            if start in valid_indexes:
                expr = match.group(1).strip()
                expr = re.sub(r"//.*$", "", expr).strip()  # strip line comments
                expr_map[start] = expr
        return expr_map

    def _detect_variable_collisions(
        self, return_expr_map: dict[int, str], command_vars: list[str]
    ) -> list[str]:
        warnings = []
        for index, expr in return_expr_map.items():
            for var in command_vars:
                if re.search(r"\b" + re.escape(var) + r"\b", expr):
                    warnings.append(
                        f"⚠️ Warning: variable '{var}' is used in both the defer command and the return expression at index {index}."
                    )
                    break
        return warnings

    def _insert_commands(self, source: str, indexes: list[int], command: str) -> str:
        insertions = {i: f"\n{command}\n" for i in indexes}
        parts = []
        last_index = 0
        for i in sorted(insertions.keys()):
            parts.append(source[last_index:i])
            parts.append(insertions[i])
            last_index = i
        parts.append(source[last_index:])
        return "".join(parts)
