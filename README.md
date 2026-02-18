# Moderation Service

A modular, Dockerized content moderation service featuring an asynchronous API, background processing, and rate limiting.

## Project Structure
- **API**: FastAPI service for content submission and status checks.
- **Processor**: Python worker for asynchronous text moderation.
- **Database**: PostgreSQL for persistent storage.
- **Redis**: Used for the task queue and rate limiting.

## Setup & Running

1. **Clone and Start**:
   ```bash
   docker-compose up --build
   ```
   
2. **Verify Installation**:
   The API will be available at `http://localhost:8000`.

## Usage

### Submit Content
```bash
curl -X POST http://localhost:8000/api/v1/content/submit \
  -H "Content-Type: application/json" \
  -d '{"userId": "alice", "text": "This is a clean post"}'
```

### Check Status
```bash
curl http://localhost:8000/api/v1/content/{content_id}/status
```

### Automated Verification
Run the included verification script (requires Python):
```bash
py verify_script.py
```

## Proof of Functionality

The following logs from `verify_script.py` demonstrate successful content submission, asynchronous moderation, and rate limiting enforcement:

```text
Waiting for API to be ready...
API is ready.

--- Submitting OK Content ---
Status: 202, Body: {'contentId': 'b205826b-a843-424f-a667-0d727df72175'}

--- Checking Status for b205826b-a843-424f-a667-0d727df72175 ---
Status: 200, Body: {'contentId': 'b205826b-a843-424f-a667-0d727df72175', 'status': 'APPROVED'}

--- Submitting Bad Content ---
Status: 202, Body: {'contentId': 'af925cef-36ad-4c14-bf0e-e88e540306c6'}

--- Checking Status for af925cef-36ad-4c14-bf0e-e88e540306c6 ---
Status: 200, Body: {'contentId': 'af925cef-36ad-4c14-bf0e-e88e540306c6', 'status': 'REJECTED'}

--- Triggering Rate Limit ---
Request 1: Status 202
Request 2: Status 202
Request 3: Status 202
Request 4: Status 202
Request 5: Status 202
Request 6: Status 202
Request 7: Status 202
Request 8: Status 202
Request 9: Status 202
Request 10: Status 202
Request 11: Status 429
Rate limit triggered successfully.
```
