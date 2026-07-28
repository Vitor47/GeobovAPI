from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    """Normalized postal address resolved from an external lookup provider."""

    street: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country_code: str
    neighborhood: str | None = None

    def to_address_line(self) -> str | None:
        """Build a single street line (street + neighborhood when present)."""
        parts = [part for part in (self.street, self.neighborhood) if part]
        if not parts:
            return None
        return ", ".join(parts)
