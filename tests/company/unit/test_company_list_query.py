import pytest
from pydantic import ValidationError

from app.presentation.api.v1.schemas.company import CompanyListQuery


@pytest.mark.unit
def test_company_list_query_strips_a_farm_name():
    params = CompanyListQuery(q="  Fazenda São João  ")

    assert params.q == "Fazenda São João"
    assert params.page == 1
    assert params.page_size == 20


@pytest.mark.unit
@pytest.mark.parametrize("value", ["100%", "a_b", "nome\\x", ""])
def test_company_list_query_rejects_or_clears_unsafe_search(value: str):
    if value == "":
        assert CompanyListQuery(q=value).q is None
        return

    with pytest.raises(ValidationError):
        CompanyListQuery(q=value)


@pytest.mark.unit
def test_company_list_query_rejects_page_size_above_the_limit():
    with pytest.raises(ValidationError):
        CompanyListQuery(page_size=101)
