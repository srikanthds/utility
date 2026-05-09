# Privacy Dashboard

A FastAPI-based web application designed to help users manage their online privacy. The dashboard provides tools to check data breaches, perform image searches, draft removal requests, and generate privacy reports.

## Features

- **Breach Check**: Search if your data appears in known data breaches
- **Image Search**: Perform reverse image searches to track photo usage online
- **Removal Drafts**: Generate templates for data removal requests
- **Search Engine Tools**: Leverage search engine capabilities for privacy research
- **Privacy Reports**: Generate comprehensive privacy reports based on search results

## Prerequisites

- Python 3.11+ (for local development)
- Docker & Docker Compose (for containerized deployment)

## Installation & Local Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd privacy-dashboard
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

The application will be available at: **http://localhost:8080**

## Docker Setup

### Prerequisites
- Docker installed
- Docker Compose installed

### Run with Docker Compose (Recommended for Development)

```bash
docker-compose up
```

The application will be available at: **http://localhost:8080**

To stop the container:
```bash
docker-compose down
```

### Build and Run with Docker (Production)

```bash
# Build the image
docker build -t privacy-dashboard .

# Run the container
docker run -p 8080:8080 privacy-dashboard
```

The application will be available at: **http://localhost:8080**

## Project Structure

```
privacy-dashboard/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database initialization
│   ├── models.py            # Data models
│   ├── routes/              # API routes
│   │   ├── setup.py         # Setup routes
│   │   ├── profile.py       # Profile management
│   │   ├── search.py        # Search functionality
│   │   ├── results.py       # Results display
│   │   └── report.py        # Report generation
│   ├── services/            # Business logic
│   │   ├── breach_check.py  # Breach checking service
│   │   ├── image_search.py  # Image search service
│   │   ├── search_engine.py # Search engine integration
│   │   └── removal_draft.py # Removal request drafting
│   ├── static/              # CSS and static files
│   └── templates/           # HTML templates
├── data/                    # Data storage
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image configuration
└── docker-compose.yml      # Docker Compose configuration
```

## Dependencies

Key Python packages:
- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Jinja2**: Template engine for HTML rendering
- **aiosqlite**: Async SQLite database support
- **httpx**: Async HTTP client
- **python-dotenv**: Environment variable management
- **ddgs**: DuckDuckGo search integration

## Configuration

You can configure the application using environment variables. Create a `.env` file in the project root:

```bash
DEBUG=False
DATABASE_URL=sqlite:///./app.db
```

## Troubleshooting

### Port Already in Use
If port 8080 is already in use, modify the port in `docker-compose.yml` or run locally with:
```bash
uvicorn app.main:app --port 8081
```

### Database Issues
The application uses SQLite stored in the `data/` directory. To reset the database, simply delete the database file and restart the application.

## License

This project is proprietary software.

## Support

For issues or questions, please refer to the project documentation or contact the development team.
