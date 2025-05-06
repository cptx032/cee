import argparse
import glob
import os
import json
from typing import Callable

from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass


@dataclass
class BaseDTO:
    name: str
    type: str


@dataclass
class CEETemplate(BaseDTO):
    template_path: str
    output: str
    context: dict | None = None

    def get_context(self) -> dict:
        context: dict = {"name": self.name}
        context.update(self.context or {})
        return context


parser = argparse.ArgumentParser()
parser.add_argument("path", default=".")
args = parser.parse_args()


def template_processor(content: dict) -> None:
    # fixme > check errors when creating the dto
    cee_template = CEETemplate(**content)

    base_dir: str = os.path.join("./cee", os.path.dirname(cee_template.template_path))
    file_name: str = os.path.basename(cee_template.template_path)
    full_template_path: str = os.path.join(base_dir, file_name)

    if not os.path.exists(full_template_path):
        print(f"Template {full_template_path} doesnt exist")
        return

    env = Environment(loader=FileSystemLoader(base_dir))
    jinja_template = env.get_template(os.path.basename(cee_template.template_path))
    # fixme > handle errors when rendering
    output_content = jinja_template.render(cee_template.get_context())
    output_path: str = os.path.join("./cee", cee_template.output)
    with open(output_path, "w") as writer:
        writer.write(output_content)


type_processors: dict[str, Callable] = {"template": template_processor}


def process_cee_file(cee_content: dict) -> None:
    required_keys: tuple[str, ...] = ("name", "type")
    for required_key in required_keys:
        if required_key not in content:
            print(f"{required_key} not found in {cee_file_name}")
            return
    cee_type: str = cee_content.get("type", "")
    if cee_type not in type_processors:
        print(f"Unknown {cee_type}")
        return
    type_processors[cee_type](content)


cee_files = os.path.join(args.path, "cee/*.cee")
for cee_file_name in glob.glob(cee_files):
    with open(cee_file_name) as cee_file:
        content: dict
        try:
            content = json.loads(cee_file.read())
        except json.decoder.JSONDecodeError:
            print(f"It was not possible to parse the file {cee_file_name}")
            continue
        process_cee_file(content)
