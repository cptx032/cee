import dataclasses
import cee_utils
from jinja2 import Environment, FileSystemLoader
import os


LINKED_LIST_TEMPLATE: str = "templates/generic_linked_list.jinja2"


@dataclasses.dataclass
class FieldDefinition:
    type: str
    name: str
    natural_key: bool = False

    def get_json(self) -> dict:
        result: dict[str, str | bool] = {
            "type": self.type,
            "name": self.name,
        }
        if self.natural_key:
            result["natural_key"] = True
        return result


def get_linked_list_source(
    name: str,
    fields: list[dict],
    include_list: list[str] | None = None,
) -> str:
    validated_fields: list[FieldDefinition] = [
        FieldDefinition(**field) for field in fields
    ]
    name = cee_utils.normalize_name(name)

    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    template = env.get_template(LINKED_LIST_TEMPLATE)
    return template.render(
        name=name,
        include_list=include_list,
        fields=[i.get_json() for i in validated_fields],
    )
