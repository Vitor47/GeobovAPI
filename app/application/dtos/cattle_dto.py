class CattleCreateDTO:
    def __init__(self, tag: str, company_id: int):
        self.tag = tag
        self.company_id = company_id


class CattleResponseDTO:
    def __init__(self, id: int, tag: str, company_id: int):
        self.id = id
        self.tag = tag
        self.company_id = company_id
