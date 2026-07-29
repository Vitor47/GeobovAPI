from dataclasses import dataclass


class CompanyCreateDTO:
    def __init__(self, name: str):
        self.name = name


class CompanyResponseDTO:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name


@dataclass
class CompanyListResultDTO:
    items: list[CompanyResponseDTO]
    total: int
    page: int
    page_size: int
    has_more: bool
