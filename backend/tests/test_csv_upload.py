"""
Test CSV upload functionality for applications
"""
import pytest
import csv
import io
from httpx import AsyncClient, ASGITransport
from app.main import app


def create_test_csv(rows: list[dict]) -> bytes:
    """Helper function to create CSV bytes from list of dicts"""
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return output.getvalue().encode('utf-8')


class TestCSVValidation:
    """Test CSV validation endpoint"""

    @pytest.mark.asyncio
    async def test_valid_csv(self):
        """Test validation with a valid CSV file"""
        rows = [
            {
                "applicant_name": "John Doe",
                "email": "john@example.com",
                "phone": "555-1234",
                "housing_type": "House",
                "motivation": "I love dogs and have experience with rescues"
            },
            {
                "applicant_name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "555-5678",
                "housing_type": "Apartment",
                "motivation": "Want a companion for my active lifestyle"
            }
        ]

        csv_content = create_test_csv(rows)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applications/csv/validate",
                files={"file": ("test_applications.csv", csv_content, "text/csv")}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["valid"] == True
            assert data["row_count"] == 2
            assert data["filename"] == "test_applications.csv"
            assert len(data["missing_columns"]) == 0

    @pytest.mark.asyncio
    async def test_missing_required_columns(self):
        """Test validation with missing required columns"""
        rows = [
            {
                "applicant_name": "John Doe",
                "email": "john@example.com"
                # Missing phone, housing_type, motivation
            }
        ]

        csv_content = create_test_csv(rows)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applications/csv/validate",
                files={"file": ("invalid.csv", csv_content, "text/csv")}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["valid"] == False
            assert "phone" in data["missing_columns"]
            assert "housing_type" in data["missing_columns"]
            assert "motivation" in data["missing_columns"]

    @pytest.mark.asyncio
    async def test_empty_csv(self):
        """Test validation with empty CSV"""
        csv_content = b"applicant_name,email,phone,housing_type,motivation\n"

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applications/csv/validate",
                files={"file": ("empty.csv", csv_content, "text/csv")}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["valid"] == False
            assert data["row_count"] == 0


class TestCSVPreview:
    """Test CSV preview endpoint"""

    @pytest.mark.asyncio
    async def test_preview_valid_csv(self):
        """Test preview with valid CSV"""
        rows = [
            {
                "applicant_name": f"Person {i}",
                "email": f"person{i}@example.com",
                "phone": f"555-{i:04d}",
                "housing_type": "House",
                "motivation": f"Motivation for person {i}"
            }
            for i in range(10)
        ]

        csv_content = create_test_csv(rows)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applications/csv/preview",
                files={"file": ("test.csv", csv_content, "text/csv")}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["total_rows"] == 10
            assert len(data["preview_rows"]) == 5  # Should return first 5 rows
            assert data["validation"]["valid"] == True


class TestCSVUploadAndIndex:
    """Test CSV upload and indexing to Elasticsearch"""

    @pytest.mark.asyncio
    async def test_upload_and_index(self):
        """Test actual upload and indexing to Elasticsearch"""
        rows = [
            {
                "applicant_name": "Test Applicant 1",
                "email": "test1@example.com",
                "phone": "555-0001",
                "housing_type": "House",
                "motivation": "I have experience with anxious dogs",
                "experience_level": "Advanced",
                "has_yard": "true"
            },
            {
                "applicant_name": "Test Applicant 2",
                "email": "test2@example.com",
                "phone": "555-0002",
                "housing_type": "Apartment",
                "motivation": "Looking for a small companion dog",
                "experience_level": "Beginner",
                "has_yard": "false"
            }
        ]

        csv_content = create_test_csv(rows)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applications/csv/upload",
                files={"file": ("test_upload.csv", csv_content, "text/csv")}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] == True
            assert data["indexed_count"] == 2
            assert data["failed_count"] == 0
            assert len(data["indexed_ids"]) > 0

            # Verify indexed document exists
            first_id = data["indexed_ids"][0]
            get_response = await client.get(f"/api/v1/applications/{first_id}")
            assert get_response.status_code == 200

    @pytest.mark.asyncio
    async def test_upload_with_malformed_data(self):
        """Test upload with some malformed rows"""
        rows = [
            {
                "applicant_name": "",  # Empty name - should fail
                "email": "invalid",
                "phone": "555-0001",
                "housing_type": "House",
                "motivation": "Test"
            },
            {
                "applicant_name": "Valid Applicant",
                "email": "valid@example.com",
                "phone": "555-0002",
                "housing_type": "Apartment",
                "motivation": "I love dogs"
            }
        ]

        csv_content = create_test_csv(rows)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/applications/csv/upload",
                files={"file": ("mixed.csv", csv_content, "text/csv")}
            )

            assert response.status_code == 200
            data = response.json()

            # At least one should succeed
            assert data["indexed_count"] >= 1


class TestElasticsearchIndexing:
    """Test Elasticsearch indexing directly"""

    @pytest.mark.asyncio
    async def test_embedding_generation(self):
        """Test that embeddings are generated during indexing"""
        from app.services.elasticsearch_client import es_client
        from app.models.es_documents import Application
        import uuid

        # Create a test application
        app_id = str(uuid.uuid4())
        doc = Application(meta={"id": app_id})

        doc.applicant_name = "Test Embedding User"
        doc.email = "embed@test.com"
        doc.phone = "555-9999"
        doc.housing_type = "House"
        doc.motivation = "I want to adopt a dog because I have experience with rescue animals"
        doc.experience_level = "Advanced"
        doc.has_yard = True
        doc.all_family_members_agree = True
        doc.has_other_pets = False

        # Save to ES (should trigger embedding generation)
        await doc.save(using=es_client.client)

        # Retrieve and verify
        retrieved = await Application.get(id=app_id, using=es_client.client)

        assert retrieved.applicant_name == "Test Embedding User"
        assert retrieved.motivation == "I want to adopt a dog because I have experience with rescue animals"

        # Clean up
        await doc.delete(using=es_client.client)

    @pytest.mark.asyncio
    async def test_semantic_search_after_upload(self):
        """Test semantic search works after CSV upload"""
        # Upload test data
        rows = [
            {
                "applicant_name": "Dog Trainer",
                "email": "trainer@example.com",
                "phone": "555-1111",
                "housing_type": "House",
                "motivation": "I am a professional dog trainer with 10 years experience"
            },
            {
                "applicant_name": "First Timer",
                "email": "first@example.com",
                "phone": "555-2222",
                "housing_type": "Apartment",
                "motivation": "Never had a dog before but really want to learn"
            }
        ]

        csv_content = create_test_csv(rows)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            upload_response = await client.post(
                "/api/v1/applications/csv/upload",
                files={"file": ("search_test.csv", csv_content, "text/csv")}
            )

            assert upload_response.status_code == 200

            # Wait a moment for indexing
            import asyncio
            await asyncio.sleep(2)

            # Search for experienced applicants
            search_response = await client.post(
                "/api/v1/applications/search",
                json={
                    "query": "professional dog trainer with lots of experience",
                    "limit": 5
                }
            )

            assert search_response.status_code == 200
            results = search_response.json()

            # Should find the trainer first
            assert len(results) > 0
            assert "trainer" in results[0]["motivation"].lower()
