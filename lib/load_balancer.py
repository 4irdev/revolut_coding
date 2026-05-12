from random import choice
from threading import Lock
from abc import ABC, abstractmethod
from typing import List, Optional

class NotPositiveServersCountError(Exception):
    pass

class MaxServersCountError(Exception):
    pass

class ServerAlreadyExistsError(Exception):
    pass

class ServerNotFoundError(Exception):
    pass

class ServerSelectionStrategy(ABC):
    @abstractmethod
    def select_server(self, instance_list: List[str]) -> str:
        raise NotImplementedError()

class RoundRobinSelectionStrategy(ServerSelectionStrategy):
    def __init__(self):
        self.index = -1

    def select_server(self, instance_list: List[str]) -> str:
        if not len(instance_list):
            raise NotPositiveServersCountError()
        self.index = (self.index + 1) % len(instance_list)
        return instance_list[self.index]

class RandomSelectionStrategy(ServerSelectionStrategy):
    def select_server(self, instance_list: List[str]) -> str:
        if not len(instance_list):
            raise NotPositiveServersCountError()
        return choice(list(instance_list))

class LoadBalancer:
    def __init__(self, max_instances: int = 10, strategy: Optional[ServerSelectionStrategy] = None):
        if max_instances <= 0:
            raise NotPositiveServersCountError()
        self.max_instances = max_instances
        self.instances: List[str] = []
        self.lock = Lock()
        self.strategy = strategy or RoundRobinSelectionStrategy()

    def register(self, instance: str) -> str:
        with self.lock:
            if len(self.instances) >= self.max_instances:
                raise MaxServersCountError()
            if instance in self.instances:
                raise ServerAlreadyExistsError()
            self.instances.append(instance)
            return instance

    def unregister(self, instance: str) -> str:
        with self.lock:
            try:
                self.instances.remove(instance)
                return instance
            except ValueError:
                raise ServerNotFoundError() from None

    def get(self) -> str:
        with self.lock:
            return self.strategy.select_server(self.instances)
