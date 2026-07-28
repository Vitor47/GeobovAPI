from dataclasses import dataclass


@dataclass
class AddressLookupRequestDTO:
    postal_code: str
    country: str


@dataclass
class AddressResponseDTO:
    street: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country_code: str
    neighborhood: str | None = None
    # Single-line street suitable for Company.address
    address_line: str | None = None
