import pytest
from pydantic import ValidationError


def test_should_create_job_with_required_fields():
    from rag_core.models import Job
    
    job = Job(job_id="test-123", state="PENDING")
    
    assert job.job_id == "test-123"
    assert job.state == "PENDING"


def test_should_fail_creating_job_without_required_fields():
    from rag_core.models import Job
    
    with pytest.raises(ValidationError):
        Job()
    
    with pytest.raises(ValidationError):
        Job(job_id="test-123")
    
    with pytest.raises(ValidationError):
        Job(state="PENDING")