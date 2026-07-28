class UnsupportedCountryError(Exception):
    """Raised when address lookup is not available for the given country."""

    def __init__(self, country_code: str) -> None:
        self.country_code = country_code
        super().__init__(
            f"Address lookup is not supported for country '{country_code}'."
        )
