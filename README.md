# Enterprise Analytics Copilot

## Business usecase
Modern organizations rely on analytics for decision-making, yet critical business metrics are often computed incorrectly due to inconsistent SQL logic, misunderstood business rules, and ungoverned ad-hoc queries.  
This leads to incorrect KPIs, wrong decisions, and real business impact.

## What This System Does
Enterprise Analytics Copilot is a backend system that allows users to ask business questions in natural language and receive **correct, explainable, and policy-compliant analytics results** from a relational database.
Unlike generic text-to-SQL systems, this project enforces business logic, metric definitions, and safety constraints **before** any query is executed.
- **Why This Project Matters**:

This project models how analytics systems should be built in production environments:  
**correctness first, explainability by design, and LLMs used as controlled components rather than sources of truth.**

## Core Design Principles
- LLMs assist with interpretation, not authority over data semantics
- Business rules are explicit, versioned, and enforced
- SQL generation is constrained, validated, and auditable
- Every answer is explainable and traceable to defined metrics

## High-Level Architecture
1. Natural language query ingestion via FastAPI
2. Intent extraction and schema validation
3. Metric registry lookup and versioned definitions
4. Query planning with enforced grain and filters
5. SQL generation with dialect awareness
6. Static and semantic SQL validation
7. Controlled execution with timeout and caching
8. Result explanation generation

## Key Features
- Strict metric and dimension enforcement
- Time-grain and aggregation validation
- SQL safety checks to prevent invalid or dangerous queries
- Versioned metric definitions using YAML
- Modular planning and execution layers
- Unit-tested core logic for correctness

## Design Guarantees
- Metrics are computed only from predefined, versioned definitions
- Invalid joins, filters, and time-grains are rejected before execution
- SQL queries are statically validated for safety and correctness
- LLM output is treated as untrusted and strictly constrained
- Every response is explainable and traceable to metadata

## Technology Stack
- Python
- FastAPI
- SQL (dialect-aware generation)
- Pytest
- YAML-based metadata registry

## Running the Project
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
