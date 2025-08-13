# TDD Test Plan for API-Driven RAG Pipeline

## Overview
This test plan follows Test-Driven Development (TDD) principles for implementing a multi-module FastAPI application that integrates with external Storm Parse API and txtai. Each test will be written first (Red), then minimal code to pass (Green), followed by refactoring.

## Architecture
```
api-rag-pipeline/
├── pyproject.toml           # Workspace root
├── uv.lock                  # Single lock file
└── packages/
    ├── rag-core/            # Data models (DTO)
    ├── storm-client/        # HTTP client for Storm Parse API
    ├── rag-engine/          # txtai vector search
    ├── rag-service/         # Async pipeline orchestration
    └── rag-api/             # FastAPI interface
```

## Test Execution Order
Follow this order strictly to maintain proper dependencies and TDD flow.

### Phase 1: Foundation Setup
- [ ] Create workspace root structure with uv
- [ ] Set up root pyproject.toml with workspace members
- [ ] Create initial test structure

### Phase 2: RAG-CORE Module Tests
Purpose: Define data models that all other modules will use.

- [x] test_should_create_job_with_required_fields
  - Test: Job requires job_id and state fields
  - Implementation: Create Job Pydantic model

- [x] test_should_create_parsed_page_with_page_number_and_content
  - Test: ParsedPage has pageNumber (int) and content (str)
  - Implementation: Create ParsedPage model

- [x] test_should_create_chunk_with_all_fields
  - Test: Chunk has id, document_id, text, page_number
  - Implementation: Create Chunk model with all fields

- [x] test_should_validate_query_request_top_k_positive
  - Test: QueryRequest.top_k must be positive integer, default 3
  - Implementation: Add Pydantic validator for top_k field

- [x] test_should_create_retrieved_chunk_with_score
  - Test: RetrievedChunk extends Chunk with score field
  - Implementation: Create RetrievedChunk model

- [x] test_should_create_final_answer_with_retrieved_context
  - Test: FinalAnswer contains query, generated_answer, and List[RetrievedChunk]
  - Implementation: Create FinalAnswer model

### Phase 3: STORM-CLIENT Module Tests
Purpose: Handle HTTP communication with external Storm Parse API.

- [x] test_should_initialize_client_with_base_url_and_token
  - Test: StormApiClient stores base_url and creates auth headers
  - Implementation: Initialize with URL and Bearer token

- [ ] test_should_upload_document_and_return_job
  - Test: upload_document() posts file and returns Job object
  - Implementation: Mock httpx response, parse JSON to Job

- [ ] test_should_handle_upload_failure_with_proper_exception
  - Test: HTTP errors raise appropriate exceptions
  - Implementation: Mock 4xx/5xx responses, test error handling

- [ ] test_should_get_job_result_with_pending_state
  - Test: get_job_result() returns Job with state="PENDING", no pages
  - Implementation: Mock pending response, return tuple (Job, None)

- [ ] test_should_get_job_result_with_completed_state_and_pages
  - Test: Completed job returns Job and List[ParsedPage]
  - Implementation: Mock completed response with pages data

- [ ] test_should_handle_timeout_gracefully
  - Test: Long-running requests timeout appropriately
  - Implementation: Add timeout parameter to httpx calls

### Phase 4: RAG-ENGINE Module Tests
Purpose: Provide vector indexing and semantic search using txtai.

- [ ] test_should_initialize_txtai_embeddings
  - Test: TxtaiEngine initializes with content=True option
  - Implementation: Create embeddings instance in __init__

- [ ] test_should_index_chunks
  - Test: index() accepts List[Chunk] and stores them
  - Implementation: Convert chunks to indexable format, build index

- [ ] test_should_search_by_query_text
  - Test: search() returns results for given query
  - Implementation: Use txtai search, map results back to chunks

- [ ] test_should_return_top_k_results_with_scores
  - Test: Results limited by top_k, include similarity scores
  - Implementation: Return List[RetrievedChunk] with scores

- [ ] test_should_handle_empty_index_search
  - Test: Search on empty index returns empty list
  - Implementation: Check index state before search

### Phase 5: RAG-SERVICE Module Tests
Purpose: Orchestrate the complete async RAG pipeline.

- [ ] test_should_chunk_pages_into_fixed_size_chunks
  - Test: _chunk_pages() splits ParsedPage content into Chunks
  - Implementation: Split text by size, assign IDs and metadata

- [ ] test_should_process_document_in_background_polling
  - Test: process_document_in_background() polls until COMPLETED
  - Implementation: Mock multiple poll responses, verify indexing

- [ ] test_should_handle_failed_job_state
  - Test: Background process stops on FAILED/ERROR state
  - Implementation: Check job state, handle failure gracefully

- [ ] test_should_track_job_states_in_memory
  - Test: Service maintains job_id -> state mapping
  - Implementation: Update self.jobs dict during processing

- [ ] test_should_answer_query_with_context
  - Test: answer_query() retrieves chunks and generates answer
  - Implementation: Search engine, synthesize answer from context

- [ ] test_should_handle_empty_index_gracefully
  - Test: Query on empty index returns informative response
  - Implementation: Check index state before search

### Phase 6: RAG-API Module Tests
Purpose: Expose REST API endpoints via FastAPI with async processing.

- [ ] test_should_upload_pdf_and_return_job_immediately
  - Test: POST /ingest returns Job with job_id immediately
  - Implementation: Start background task, return job info

- [ ] test_should_trigger_background_processing_on_upload
  - Test: Upload triggers async processing in background
  - Implementation: Use FastAPI BackgroundTasks

- [ ] test_should_get_job_status_by_id
  - Test: GET /ingest/status/{job_id} returns current state
  - Implementation: Query service job tracking

- [ ] test_should_return_404_for_unknown_job_id
  - Test: Unknown job_id returns 404 error
  - Implementation: Check job exists before returning

- [ ] test_should_query_via_post_endpoint
  - Test: POST /query accepts QueryRequest, returns FinalAnswer
  - Implementation: Call service.answer_query()

- [ ] test_should_save_uploaded_file_to_disk
  - Test: Uploaded files saved to temp directory
  - Implementation: Write UploadFile content to disk

- [ ] test_should_return_422_for_invalid_query_request
  - Test: Invalid request body returns 422
  - Implementation: FastAPI automatic validation

### Phase 7: Integration Tests
Purpose: Validate complete system behavior.

- [ ] test_end_to_end_pdf_upload_poll_and_query
  - Test: Upload PDF, poll for completion, query returns answers
  - Implementation: Mock external API, test full flow

- [ ] test_async_job_processing_workflow
  - Test: Background job processes while API remains responsive
  - Implementation: Test concurrent requests during processing

- [ ] test_multiple_document_handling
  - Test: System handles multiple PDFs with separate jobs
  - Implementation: Track multiple job_ids independently

- [ ] test_resilient_polling_with_retries
  - Test: Polling continues despite temporary failures
  - Implementation: Mock intermittent API errors

## Test Naming Convention
All tests follow the pattern:
```
test_should_[expected_behavior]_when_[condition]
```

## Mocking Strategy
- External Storm API: Mock HTTP responses with httpx_mock
- Job states: Simulate PENDING -> PROCESSING -> COMPLETED flow
- PDF files: Use minimal test fixtures
- txtai: Mock for unit tests, real for integration
- Async operations: Use pytest-asyncio for async test support

## Success Criteria
- All tests pass
- Each test drives minimal implementation
- Clear separation of concerns between modules
- No implementation without failing test first
- Refactor only with green tests

## Implementation Notes
1. Start with the first unmarked test
2. Write the test first (it should fail)
3. Implement only enough code to pass
4. Run all tests to ensure nothing broke
5. Refactor if needed (with all tests green)
6. Mark test as complete
7. Commit with descriptive message
8. Move to next test

## Key Implementation Details
- All modules use `uv` native build backend (no hatchling)
- HTTP client uses `httpx` for async operations
- Background tasks use FastAPI's BackgroundTasks
- Job polling interval: 5 seconds
- Chunk size: 500 characters
- Default top_k: 3 results