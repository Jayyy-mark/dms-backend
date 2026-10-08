from dataclasses import dataclass


@dataclass
class UserRoleResponseContract:
    id: int
    name: str


@dataclass
class UserRoleCreateContract:
    name: str
