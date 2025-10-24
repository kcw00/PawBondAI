import pytest
from unittest.mock import MagicMock, ANY
from app.services.bigquery_service import BigQueryService


@pytest.fixture
def mock_bq_client(mocker):
    """Mocks the google.cloud.bigquery.Client"""
    mock = MagicMock()
    # Mock the chain of calls: client.query(...).result()
    mock.query.return_value.result.return_value = [
        {"adopter_experience_level": "expert", "success_rate": 95.5}
    ]
    mocker.patch("app.services.bigquery_service.bigquery.Client", return_value=mock)
    return mock


@pytest.mark.asyncio
async def test_query_success_rates_with_filters(mock_bq_client):
    """
    Tests that the query method builds the correct SQL and parameters.
    """
    service = BigQueryService()
    filters = {"adopter_experience_level": "expert"}

    result = await service.query_success_rates(filters)

    # Assert the output
    assert len(result["stats"]) == 1
    assert result["stats"][0]["success_rate"] == 95.5

    # Assert that the client was called correctly
    # This is the most important part of the test!
    mock_bq_client.query.assert_called_once()

    # Check the generated SQL query
    called_args, called_kwargs = mock_bq_client.query.call_args
    generated_sql = called_args[0]
    job_config = called_kwargs["job_config"]

    # Check that the SQL contains the correct clauses
    assert "adopter_experience_level = @exp_level" in generated_sql
    assert (
        "dog_difficulty_level = @dog_diff" not in generated_sql
    )  # Check that unused filters are not added

    # Check that the parameters are correct
    param_dict = {p.name: p.value for p in job_config.query_parameters}
    assert param_dict["exp_level"] == "expert"
