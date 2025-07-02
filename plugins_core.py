import abc
import cee_core


class BasePlugin(abc.ABC):
    names: list[str] = []
    description: str = ""

    def __init__(self, command: cee_core.CeeCommand) -> None:
        self.command: cee_core.CeeCommand = command
        if not self.names:
            raise TypeError("Class should define 'names' attribute")

    @abc.abstractmethod
    def is_command_valid(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_proposed_changes(self) -> cee_core.SourceCodeChanges:
        raise NotImplementedError
