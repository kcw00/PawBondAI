import re
from typing import Dict, Any, Optional, List
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
from app.core.config import get_settings
from app.core.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


class DocumentAIService:
    """
    Google Cloud Document AI service for processing scanned MEDICAL RECORDS.
    Extracts structured data from PDFs and images of vet records.
    """

    def __init__(self):
        self.project_id = settings.gcp_project_id
        self.location = settings.gcp_region
        self.processor_id = settings.doc_ai_processor_id
        if not self.processor_id:
            logger.critical("Document AI Processor ID is not configured in settings!")
            raise ValueError("DOC_AI_PROCESSOR_ID must be set")

        opts = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
        self.client = documentai.DocumentProcessorServiceClient(client_options=opts)
        self.processor_name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )

    def process_medical_record(
        self, file_content: bytes, mime_type: str = "application/pdf"
    ) -> Dict[str, Any]:
        """
        Process a medical record (PDF or image) and extract structured data.
        This is the main public method for this service.
        """
        try:
            raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
            request = documentai.ProcessRequest(name=self.processor_name, raw_document=raw_document)

            result = self.client.process_document(request=request)
            document = result.document

            mapped_data = self._parse_and_map_document(document)

            logger.info("Successfully processed medical document with Document AI")
            return mapped_data

        except Exception as e:
            logger.error(f"Error processing medical document with Document AI: {e}")
            raise

    def _parse_and_map_document(self, document: documentai.Document) -> Dict[str, Any]:
        """
        Orchestrates the extraction, normalization, and mapping of the document's content.
        """
        normalized_fields = {}
        # Extract all key-value pairs found by the Form Parser
        for page in document.pages:
            for form_field in page.form_fields:
                field_name = self._get_field_text(form_field.field_name, document.text)
                field_value = self._get_field_text(form_field.field_value, document.text)

                normalized_name = self._normalize_medical_field_name(field_name)

                if normalized_name and field_value:
                    normalized_fields[normalized_name] = field_value

        # Map these normalized fields to our final, structured ES schema
        return self._map_to_medical_schema(normalized_fields, document.text)

    def _get_field_text(self, field, full_text: str) -> str:
        """Helper to extract text from a document AI field's text anchor."""
        if not field or not field.text_anchor or not field.text_anchor.text_segments:
            return ""

        return "".join(
            full_text[int(segment.start_index) : int(segment.end_index)]
            for segment in field.text_anchor.text_segments
        ).strip()

    def _normalize_medical_field_name(self, field_name: str) -> Optional[str]:
        """
        Normalizes field names found on vet records to our standard keys.
        This is the "dictionary" that translates messy real-world labels.
        """
        field_name = field_name.lower().strip().replace(":", "")

        field_mapping = {
            "vet_clinic_name": ["clinic", "hospital", "veterinary", "vet"],
            "visit_date": ["date of visit", "date", "visit on"],
            "weight": ["weight", "wt."],
            "spay_neuter_status": ["spay", "neuter", "altered", "sterilized", "sex"],
            "rabies_vaccine": ["rabies"],
            "dhpp_vaccine": ["dhpp", "dapp", "da2pp", "distemper", "parvo"],
            "bordetella_vaccine": ["bordetella", "kennel cough"],
            "heartworm_test": ["heartworm", "hw test", "4dx"],
            "fecal_test": ["fecal", "stool sample"],
        }

        for standard_name, variations in field_mapping.items():
            if any(var in field_name for var in variations):
                return standard_name
        return None

    def _map_to_medical_schema(self, extracted_fields: dict, raw_text: str) -> dict:
        """
        Takes the normalized key-value pairs and the full text, and builds the
        final dictionary for indexing in Elasticsearch.
        """
        return {
            "document_text": raw_text,
            "visit_date": self._find_visit_date(extracted_fields, raw_text),
            "vet_clinic_name": extracted_fields.get("vet_clinic_name"),
            "weight_kg": self._parse_weight(extracted_fields.get("weight")),
            "spay_neuter_status": self._find_spay_neuter_status(extracted_fields),
            "vaccinations": self._parse_vaccinations(extracted_fields),
            # You can add similar parsers for procedures and medications in the future
            "procedures": [],
            "medications": [],
            "extracted_key_values": extracted_fields,
        }

    # --- Specific Data Parsing Helper Functions ---

    def _find_visit_date(self, fields: dict, raw_text: str) -> Optional[str]:
        """Finds and formats a date from fields or raw text."""
        if date_str := fields.get("visit_date"):
            # TODO: Implement robust date parsing (e.g., using dateutil.parser)
            # For now, we return the raw string.
            return date_str
        # TODO: Fallback to regex on raw_text if the field isn't found.
        return None

    def _parse_weight(self, weight_str: Optional[str]) -> Optional[float]:
        """Parses weight string (e.g., '10.5 kg' or '22 lbs') into kg."""
        if not weight_str:
            return None
        try:
            # Find the first number (integer or float) in the string
            weight_val = float(re.findall(r"[\d.]+", weight_str)[0])
            if "lbs" in weight_str.lower():
                return round(weight_val * 0.453592, 2)  # Convert lbs to kg
            return weight_val
        except (ValueError, TypeError, IndexError):
            # Return None if no number is found or conversion fails
            return None

    def _find_spay_neuter_status(self, fields: dict) -> str:
        """Determines if the animal is spayed/neutered from the document."""
        if status_text := fields.get("spay_neuter_status"):
            status_text = status_text.lower()
            if any(
                term in status_text for term in ["yes", "done", "complete", "neutered", "spayed"]
            ):
                return "Completed"
            if any(term in status_text for term in ["no", "intact"]):
                return "Intact"
        return "Unknown"

    def _parse_vaccinations(self, fields: dict) -> List[Dict[str, Any]]:
        """Parses all known vaccination fields into a list of nested objects."""
        vaccinations = []
        # Maps the standard vaccine name to the normalized field key we look for
        vaccine_keys = {
            "Rabies": "rabies_vaccine",
            "DHPP": "dhpp_vaccine",
            "Bordetella": "bordetella_vaccine",
        }
        for vax_name, field_key in vaccine_keys.items():
            # The value of the field is often the date it was administered
            if date_administered := fields.get(field_key):
                vaccinations.append(
                    {
                        "name": vax_name,
                        # TODO: Implement robust date parsing for this value
                        "date_administered": date_administered,
                    }
                )
        return vaccinations


# Singleton instance for use across the application
document_ai_service = DocumentAIService()
