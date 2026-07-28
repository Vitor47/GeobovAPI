from __future__ import annotations

from typing import Any

from app.domain.entities.address import Address

_BRAZIL_COUNTRY_CODE = "BR"


def normalize_brazilian_cep(postal_code: str) -> str | None:
    """
    Strip non-digits from a Brazilian CEP and validate length.

    Args:
        postal_code: Raw CEP string (may include hyphen/spaces).

    Returns:
        Eight-digit CEP, or None when invalid.
    """
    digits = "".join(ch for ch in postal_code if ch.isdigit())
    if len(digits) != 8:
        return None
    return digits


def format_brazilian_cep(digits: str) -> str:
    """Format an 8-digit CEP as NNNNN-NNN."""
    return f"{digits[:5]}-{digits[5:]}"


def map_via_cep_response(payload: dict[str, Any]) -> Address | None:
    """
    Anti-corruption layer: translate ViaCEP JSON into the domain Address.

    ViaCEP returns ``{"erro": true}`` for unknown CEPs.

    Args:
        payload: Raw JSON object from ViaCEP.

    Returns:
        Domain Address, or None when ViaCEP reports an error / empty city.
    """
    if payload.get("erro") is True:
        return None

    city = _clean(payload.get("localidade"))
    if not city:
        return None

    street = _clean(payload.get("logradouro"))
    neighborhood = _clean(payload.get("bairro"))
    state = _clean(payload.get("uf"))
    cep = _clean(payload.get("cep"))
    postal_code = cep
    if cep:
        digits = normalize_brazilian_cep(cep)
        if digits:
            postal_code = format_brazilian_cep(digits)

    return Address(
        street=street,
        city=city,
        state=state,
        postal_code=postal_code,
        country_code=_BRAZIL_COUNTRY_CODE,
        neighborhood=neighborhood,
    )


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
