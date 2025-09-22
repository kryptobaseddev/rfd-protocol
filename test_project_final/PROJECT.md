# Test Project for RFD Verification

## Overview
This is a simple web application to test the Reality-First Development Protocol in action. We'll build a basic task management system to verify RFD actually prevents hallucination and drift.

## Features

### Feature 1: Task Creation API
**Description**: REST API endpoint to create new tasks
**Acceptance Criteria**:
- POST /tasks endpoint accepts JSON: {"title": "string", "description": "string"}
- Returns task with ID and created timestamp
- Persists to file-based storage (tasks.json)
- Returns 400 for invalid input

### Feature 2: Task List Retrieval
**Description**: REST API endpoint to retrieve all tasks  
**Acceptance Criteria**:
- GET /tasks endpoint returns array of all tasks
- Each task includes id, title, description, created_at
- Returns empty array if no tasks exist
- Response is valid JSON

### Feature 3: Basic Web Interface
**Description**: Simple HTML page to view and add tasks
**Acceptance Criteria**:
- Static HTML file served at /
- Form to add new task (title + description)
- List showing all existing tasks
- Form submission creates task via API

## Technology Stack
- Python Flask for REST API
- JSON file for data storage
- Simple HTML/JS for frontend
- No external databases required

## Success Metrics
- All 3 features working end-to-end
- Real data flowing through system
- No mocked responses or stub functions
- Deployable to production