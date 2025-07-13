import re
import json
import cee_core
import plugins_core
import cee_utils


class Plugin(plugins_core.BasePlugin):
    names: list[str] = ["with"]
    description: str = (
        "Responsible for automatic resource management with cleanup, "
        "similar to Python's with statement"
    )

    # Global mapping storage
    _resource_mappings = {
        "open": {"type": "int", "deallocator": "close"},
        "fopen": {"type": "FILE*", "deallocator": "fclose"},
        "opendir": {"type": "DIR*", "deallocator": "closedir"},
        "pipe": {"type": "int", "deallocator": "close"},
        "malloc": {"type": "void*", "deallocator": "free"},
        "calloc": {"type": "void*", "deallocator": "free"},
        "realloc": {"type": "void*", "deallocator": "free"},
        "aligned_alloc": {"type": "void*", "deallocator": "free"},
        "posix_memalign": {"type": "void*", "deallocator": "free"},
        "mmap": {"type": "void*", "deallocator": "munmap"},
        "socket": {"type": "int", "deallocator": "close"},
        "accept": {"type": "int", "deallocator": "close"},
        "sem_init": {"type": "int", "deallocator": "sem_destroy"},
        "pthread_mutex_init": {"type": "int", "deallocator": "pthread_mutex_destroy"},
        "pthread_cond_init": {"type": "int", "deallocator": "pthread_cond_destroy"},
        "dlopen": {"type": "void*", "deallocator": "dlclose"},
        "tmpfile": {"type": "FILE*", "deallocator": "close"},
    }

    def is_command_valid(self) -> bool:
        return bool(self.command.arguments.strip())

    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        arguments = self.command.arguments.strip()

        # Check if this is a set-map operation
        if arguments.startswith("set-map"):
            return self._handle_set_map()
        return self._handle_with_statement()

    def _handle_set_map(self) -> cee_core.SourceCodeChanges:
        """Handle @with set-map command to update resource mappings"""
        try:
            # Extract the mapping part after "set-map"
            mapping_str = self.command.arguments.strip()
            if mapping_str.startswith("set-map"):
                mapping_str = mapping_str[8:].strip()  # Remove "set-map" prefix

            # Parse the JSON mapping from the body
            body_content = self.command.body.strip()
            if body_content.startswith("{") and body_content.endswith("}"):
                mapping = json.loads(body_content)
            else:
                # Handle simple key-value pairs for backward compatibility
                mapping = {}
                pairs = body_content.split(",")
                for pair in pairs:
                    if ":" in pair:
                        key, value = pair.split(":", 1)
                        key = key.strip().strip('"')
                        value = value.strip().strip('"')
                        # Convert simple string to new format
                        mapping[key] = {"type": "void*", "deallocator": value}

            # Update global mappings
            Plugin._resource_mappings.update(mapping)

            # Return empty changes since this is just configuration
            return cee_core.SourceCodeChanges(replacement_text="")

        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid mapping format: {e}")

    def _handle_with_statement(self) -> cee_core.SourceCodeChanges:
        """Handle @with command for resource management."""
        body_source = self.command.body[1:-1]  # Remove outer braces
        arguments = self.command.arguments.strip()

        # Parse the with statement: open("file", "r") as my_file
        match = re.match(r"(\w+)\s*\((.*?)\)\s+as\s+(\w+)", arguments)
        if not match:
            raise ValueError(f"Invalid with statement format: {arguments}")

        open_func = match.group(1)
        open_args = match.group(2)
        var_name = match.group(3)

        # Get the corresponding mapping
        mapping = Plugin._resource_mappings.get(open_func)
        if not mapping:
            raise ValueError(f"No mapping found for function '{open_func}'")

        # Extract type and deallocator
        var_type = mapping["type"]
        close_func = mapping["deallocator"]

        # Generate the variable declaration and assignment
        var_declaration = f"{var_type} {var_name} = {open_func}({open_args});"

        # Generate the close call
        close_call = f"{close_func}({var_name});"

        new_body = var_declaration + "\n" + body_source + "\n" + close_call

        return cee_core.SourceCodeChanges(
            replacement_text=cee_utils.add_semicolons_to_source(new_body)
        )
