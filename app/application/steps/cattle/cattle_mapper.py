from app.application.dtos.cattle_dto import CattleResponseDTO


def cattle_to_response_dto(cattle) -> CattleResponseDTO:
    return CattleResponseDTO(
        id=cattle.id,
        tag=cattle.tag,
        name=cattle.name,
        company_id=cattle.company_id,
        is_active=cattle.is_active,
        description=cattle.description,
        birth_date=cattle.birth_date,
        weight=cattle.weight,
        breed=cattle.breed,
        gender=cattle.gender,
        color=cattle.color,
        notes=cattle.notes,
    )
