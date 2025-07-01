from typing import Any, cast
import cee_core
import json
import linked_list_utils as llu

"""
Usage:

@ll StringList {
    "value": "char*",
    "natural_keys": ["value"]
}
"""


class Plugin:
    name: str | list[str] = ["ll", "linkedlist"]
    # fixme > when finding a bool field, include the stdbool in the include list
    allowed_types: tuple[str, ...] = ("char*", "float", "double", "int", "bool")
    description: str = "Creates a linked list with the specified fields"

    @staticmethod
    def get_ll_name(command: cee_core.CeeCommand) -> str:
        name: str = command.arguments.strip()
        if not name:
            raise ValueError("Empty linked list name")
        if len(name.split()) > 1:
            raise ValueError("Invalid linked list name")
        return name

    @staticmethod
    def get_parsed_json(command: cee_core.CeeCommand) -> Any | None:
        try:
            return json.loads(command.body)
        except json.decoder.JSONDecodeError:
            pass
        return None

    @staticmethod
    def get_fields(command: cee_core.CeeCommand) -> list | None:
        json_fields: Any = Plugin.get_parsed_json(command)
        if not json_fields:
            return None

        if type(json_fields) is not dict:
            return None

        final_format_fields: list = []
        natural_keys: list[str] = json_fields.get("natural_keys", [])
        for field_name in json_fields:
            if field_name == "natural_keys":
                continue

            field_value = json_fields[field_name]
            field_item: dict = {"name": field_name, "type": field_value}
            if field_name in natural_keys:
                field_item["natural_key"] = True
            final_format_fields.append(field_item)
        return final_format_fields

    @staticmethod
    def is_command_valid(command: cee_core.CeeCommand) -> bool:
        fields: list | None = Plugin.get_fields(command)
        if not fields:
            return False

        for field in fields:
            field_type = field["type"]
            if type(field_type) is not str:
                return False
            if field_type not in Plugin.allowed_types:
                return False
        return True

    @staticmethod
    def get_proposed_changes(
        command: cee_core.CeeCommand,
    ) -> cee_core.SourceCodeChanges:
        return cee_core.SourceCodeChanges(
            replacement_text=llu.get_linked_list_source(
                name=Plugin.get_ll_name(command),
                fields=cast(list, Plugin.get_fields(command)),
            )
        )
