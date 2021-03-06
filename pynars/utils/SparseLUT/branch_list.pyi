import typing
from copy import copy as copy, deepcopy as deepcopy
from typing import Any, Callable, Dict, List, Set, Type

deepcopy2: Any

class DictList:
    dict: Dict[tuple, Dict[int, Type['Node']]]
    len: int
    def __init__(self) -> None: ...
    def __getitem__(self, key): ...
    def __setitem__(self, key, value) -> None: ...
    def __len__(self): ...
    def values(self) -> List['Node']: ...
    def pop(self, key, default: Any | None = ...): ...
    def pop_identical(self, key, id, default: Any | None = ...): ...

class Node:
    next_nodes: DictList
    last_nodes: DictList
    is_end: bool
    index: Set[int]
    depth: int
    def __init__(self, index: set, is_end: bool = ..., depth: int = ..., next_nodes: typing.OrderedDict[tuple, 'Node'] = ..., last_nodes: typing.OrderedDict[tuple, 'Node'] = ...) -> None: ...
    def append(self, node: Type['Node']): ...
    def duplicate_shallow(self, index: set = ..., enable_last_nodes: bool = ...): ...
    def duplicate_deep(self, index: set = ...): ...
    def remove_next(self, node: Type['Node'], identical: bool = ...): ...
    def remove_last(self, node: Type['Node'], identical: bool = ...): ...
    def reset_index(self, index): ...
    @property
    def is_fan_in(self): ...
    @property
    def next_nodes_list(self): ...
    @property
    def last_nodes_list(self): ...
    def __getitem__(self, i): ...
    def __setitem__(self, i, value) -> None: ...

class BranchList:
    blists: Node
    shape: tuple
    depth: int
    lists: list
    def __init__(self, shape: tuple) -> None: ...
    def add(self, indices: list, value): ...
    def build(self, value_func: Callable = ..., add_func: Callable = ...): ...
    def clear(self) -> None: ...
    def draw(self, blists: List[Node] = ..., show_labels: bool = ...): ...
