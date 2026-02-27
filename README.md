# NLP Insight API 🚀

A production-ready FastAPI application for Text Analysis and Sentiment Classification. This project demonstrates modern backend engineering practices, including **Dependency Injection**, **Containerization (Docker)**, **Automated Testing**, and **MLOps logging**.

## 🌟 Key Features

* **Sentiment Analysis Engine**: A simulated AI engine that classifies text as POSITIVE, NEGATIVE, or NEUTRAL.
* **Data Validation**: Strict input validation using Pydantic (min/max length constraints).
* **MLOps Persistence**: Every prediction is logged into an SQLite database for future model retraining and monitoring.
* **Monitoring Dashboard**: Dedicated endpoint to track model performance and sentiment distribution.
* **Containerized Architecture**: Fully Dockerized for "plug-and-play" deployment.
* **Automated Testing**: Comprehensive test suite using `pytest` and `TestClient`.

## 🛠 Tech Stack

* **Framework**: FastAPI
* **Data Validation**: Pydantic
* **Database**: SQLite3
* **Testing**: Pytest & HTTPX
* **Containerization**: Docker
* **Server**: Uvicorn

## 🚀 Quick Start (Commands)

Follow these steps to build, test, and run the application using Docker:

### 1. Build the Docker Image
```bash
docker build -t nlp-api .
```
### 2. Run Automated Tests
```bash
docker run --rm nlp-api pytest
```
### 3. Run the Application Container
```bash
docker run -p 8000:8000 nlp-api
```
### 4. Access the API & Documentation
Interactive Swagger UI: http://localhost:8000/docs
Monitoring Stats Dashboard: http://localhost:8000/monitoring/stats

## 📊 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | /analyze/ | Processes text and returns sentiment with confidence score. |
| GET | /monitoring/stats | Returns total predictions and sentiment distribution. |
| GET | /docs | Interactive Swagger UI documentation. |

## 🏗 Project Structure

```text
├── main.py          # FastAPI application & endpoints
├── engine.py        # Logic for Sentiment Analysis (Mock AI)
├── schemas.py       # Pydantic models for Request/Response
├── database.py      # SQLite connection & DB initialization
├── test_main.py     # Unit and Integration tests
├── Dockerfile       # Container configuration
└── requirements.txt # Project dependencies
```