import pytest
from unittest.mock import MagicMock

from app.services.document_ai_service import DocumentAIService
from google.cloud.documentai_v1 import types as documentai_types


@pytest.fixture
def mock_docai_client(mocker):
    """Mocks the DocumentProcessorServiceClient for medical records."""
    mock_client = MagicMock()
    mock_client.processor_path.return_value = (
        "projects/mock-project/locations/us/processors/mock-id"
    )

    # --- Build a FAKE medical record response ---
    full_text = (
        "Happy Paws Vet Clinic\nDate: Jan 15, 2024\n"
        "Patient: Fido\nWeight: 22 lbs\n"
        "Services:\n - Rabies Vaccine: Given\n - Spay/Neuter: Yes, done\n"
    )

    # Helper to dynamically find indices, making the test robust
    def get_segment(text_to_find):
        start = full_text.find(text_to_find)
        end = start + len(text_to_find)
        return documentai_types.Document.TextAnchor.TextSegment(start_index=start, end_index=end)

    fake_form_fields = [
        # Field for Clinic Name
        documentai_types.Document.Page.FormField(
            field_name=documentai_types.Document.Page.Layout(
                text_anchor=documentai_types.Document.TextAnchor(
                    text_segments=[get_segment("Happy Paws Vet Clinic")]
                )
            ),
            # In this fake document, the name is a header, so it has no "value"
            field_value=documentai_types.Document.Page.Layout(text_anchor=None),
        ),
        # Field for Date
        documentai_types.Document.Page.FormField(
            field_name=documentai_types.Document.Page.Layout(
                text_anchor=documentai_types.Document.TextAnchor(
                    text_segments=[get_segment("Date:")]
                )
            ),
            field_value=documentai_types.Document.Page.Layout(
                text_anchor=documentai_types.Document.TextAnchor(
                    text_segments=[get_segment("Jan 15, 2024")]
                ),
                confidence=0.99,
            ),
        ),
        # Field for Weight
        documentai_types.Document.Page.FormField(
            field_name=documentai_types.Document.Page.Layout(
                text_anchor=documentai_types.Document.TextAnchor(
                    text_segments=[get_segment("Weight:")]
                )
            ),
            field_value=documentai_types.Document.Page.Layout(
                text_anchor=documentai_types.Document.TextAnchor(
                    text_segments=[get_segment("22 lbs")]
                ),
                confidence=0.98,
            ),
        ),
        # Field for Rabies Vaccine
        documentai_types.Document.Page.FormField(
            field_name=documentai_types.Document.Page.Layout(
                text_anchor=documentai_types.Document.TextAnchor(
                    text_segments=[get_segment("Rabies Vaccine:")]
                )
            ),
            field_value=documentai_types.Document.Page.Layout(
                text_anchor=documentai_types.Document.TextAnchor(
                    text_segments=[get_segment("Given")]
                ),
                confidence=0.95,
            ),
        ),
        # Field for Spay/Neuter
        documentai_types.Document.Page.FormField(
            field_name=documentai_types.Document.Page.Layout(
                text_anchor=documentai_types.Document.TextAnchor(
                    text_segments=[get_segment("Spay/Neuter:")]
                )
            ),
            field_value=documentai_types.Document.Page.Layout(
                text_anchor=documentai_types.Document.TextAnchor(
                    text_segments=[get_segment("Yes, done")]
                ),
                confidence=0.97,
            ),
        ),
    ]

    fake_document = documentai_types.Document(
        text=full_text, pages=[documentai_types.Document.Page(form_fields=fake_form_fields)]
    )
    fake_process_response = documentai_types.ProcessResponse(document=fake_document)
    mock_client.process_document.return_value = fake_process_response

    mocker.patch(
        "app.services.document_ai_service.documentai.DocumentProcessorServiceClient",
        return_value=mock_client,
    )
    yield mock_client


def test_process_medical_record_happy_path(mock_docai_client):
    """
    Tests the main service method with a mocked API response to verify
    the full extraction and mapping pipeline for a medical record.
    """
    # ARRANGE
    service = DocumentAIService()
    dummy_file_content = b"fake pdf bytes"

    # ACT
    result = service.process_medical_record(dummy_file_content)

    # ASSERT
    # Verify that the final mapped data is correct
    assert result["document_text"] is not None
    assert result["visit_date"] == "Jan 15, 2024"

    # Test the parsing logic for weight (conversion from lbs to kg)
    assert result["weight_kg"] == pytest.approx(9.98)

    # Test the parsing logic for status
    assert result["spay_neuter_status"] == "Completed"

    # Test the nested object creation for vaccinations
    assert len(result["vaccinations"]) == 1
    assert result["vaccinations"][0]["name"] == "Rabies"
    assert result["vaccinations"][0]["date_administered"] == "Given"

    # Verify the raw extracted fields were captured
    assert "weight" in result["extracted_key_values"]
    assert result["extracted_key_values"]["weight"] == "22 lbs"
