# tests/services/test_sentiment_service.py

import pytest
from unittest.mock import MagicMock
from app.services.sentiment_service import SentimentService
from google.cloud.language_v1.types import (
    Sentiment,
    Entity,
    AnalyzeSentimentResponse,
    AnalyzeEntitiesResponse,
)


@pytest.fixture
def mock_google_nlp_client(mocker):
    """Mocks the google.cloud.language_v1.LanguageServiceClient"""
    # Create a mock object that will replace the real client
    mock_client = MagicMock()

    # --- Configure the FAKE sentiment response ---
    fake_sentiment = Sentiment(score=0.8, magnitude=3.5)
    mock_client.analyze_sentiment.return_value = AnalyzeSentimentResponse(
        document_sentiment=fake_sentiment
    )

    # --- Configure the FAKE entities response ---
    fake_entities = [
        Entity(name="forever home", type="OTHER", salience=0.9),
        Entity(name="rescue dogs", type="OTHER", salience=0.8),
        Entity(name="work from home", type="EVENT", salience=0.7),
    ]
    mock_client.analyze_entities.return_value = AnalyzeEntitiesResponse(entities=fake_entities)

    mocker.patch(
        "app.services.sentiment_service.language_v1.LanguageServiceClient", return_value=mock_client
    )
    return mock_client


def test_analyze_application_motivation_strong_candidate(mock_google_nlp_client):
    """
    GIVEN a positive motivation text
    WHEN analyze_application_motivation is called
    THEN it should return a 'Highly Recommended' assessment
    """

    service = SentimentService()

    sample_text = (
        "We are so excited for the opportunity to provide a forever home. "
        "We have experience with rescue dogs and work from home. This is a lifetime commitment."
    )

    # Call the method we want to test
    result = service.analyze_application_motivation(sample_text)

    assert (
        result["recommendation"]
        == "Highly Recommended - Strong commitment signals and positive sentiment"
    )
    assert result["sentiment"]["score"] == pytest.approx(0.8)
    assert result["sentiment"]["interpretation"] == "Highly Positive & Enthusiastic"
    assert result["commitment_assessment"]["commitment_level"] == "Very High"
    assert "long_term_commitment" in result["key_themes"]
    assert "experienced_adopter" in result["key_themes"]

    mock_google_nlp_client.analyze_sentiment.assert_called_once()
    mock_google_nlp_client.analyze_entities.assert_called_once()
