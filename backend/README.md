# Contract Intelligence Parser Backend

A FastAPI-based backend service for automated contract analysis and data extraction.

## Features

- **PDF Contract Upload**: Drag-and-drop file upload with validation
- **Async Processing**: Background contract parsing using Celery
- **Data Extraction**: Comprehensive extraction of contract elements:
  - Party identification and roles
  - Financial details and line items
  - Payment terms and structure
  - Service Level Agreements (SLA)
  - Contact and account information
  - Revenue classification
- **Scoring System**: Weighted scoring algorithm (0-100 points)
- **Gap Analysis**: Identification of missing critical fields
- **RESTful API**: Complete CRUD operations for contract management
- **Real-time Status**: Track processing progress and status
- **File Management**: Secure file storage and download

## Technology Stack

- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **Task Queue**: Celery with Redis broker
- **PDF Processing**: pdfplumber for text extraction
- **Environment Management**: UV package manager
- **Testing**: pytest with coverage reporting
- **Containerization**: Docker and Docker Compose

## Project Structure

```
backend/
├── src/
│   ├── api/                # API routes and endpoints
│   ├── core/              # Configuration and utilities
│   ├── database/          # MongoDB models and connection
│   ├── services/          # Business logic and extraction
│   ├── tasks/             # Celery async tasks
│   └── main.py           # FastAPI application
├── tests/                # Unit tests
├── .env                  # Environment variables
├── pyproject.toml       # UV project configuration
├── Dockerfile           # Container definition
├── docker-compose.yml   # Multi-service setup
└── README.md           # This file
```

## Quick Start

### Prerequisites

- Python 3.13+
- UV package manager
- Docker and Docker Compose (for containerized setup)
- MongoDB and Redis (if running locally)

### Local Development Setup

1. **Clone and navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Install UV** (if not already installed):
   ```bash
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Update MongoDB and Redis URLs if needed
   ```bash
   cp .env.example .env
   ```

5. **Start required services** (MongoDB and Redis):
   ```bash
   # Using Docker
   docker run -d --name mongodb -p 27017:27017 mongo:latest
   docker run -d --name redis -p 6379:6379 redis:latest
   ```

6. **Start the Celery worker** (in a separate terminal):
   ```bash
   uv run celery
   ```

7. **Start the API server**:
   ```bash
   uv run start
   ```

8. **Access the application**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/api/v1/health

### Docker Setup (Recommended)

1. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   - API: http://localhost:8000
   - MongoDB: localhost:27017
   - Redis: localhost:6379

## API Endpoints

### Contract Management

- `POST /api/v1/contracts/upload` - Upload contract PDF
- `GET /api/v1/contracts/{id}/status` - Check processing status
- `GET /api/v1/contracts/{id}` - Get extracted contract data
- `GET /api/v1/contracts` - List all contracts (paginated)
- `GET /api/v1/contracts/{id}/download` - Download original file
- `DELETE /api/v1/contracts/{id}` - Delete contract

### System

- `GET /api/v1/health` - Health check
- `GET /api/v1/contracts/stats` - Processing statistics

## Usage Examples

### Upload a Contract

```bash
curl -X POST "http://localhost:8000/api/v1/contracts/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@contract.pdf"
```

Response:
```json
{
  "contract_id": "abc123-def456-ghi789",
  "message": "Contract uploaded successfully and processing started",
  "filename": "contract.pdf"
}
```

### Check Processing Status

```bash
curl "http://localhost:8000/api/v1/contracts/abc123-def456-ghi789/status"
```

Response:
```json
{
  "contract_id": "abc123-def456-ghi789",
  "status": "processing",
  "progress": 75,
  "filename": "contract.pdf",
  "upload_date": "2024-01-01T10:00:00"
}
```

### Get Extracted Data

```bash
curl "http://localhost:8000/api/v1/contracts/abc123-def456-ghi789"
```

Response:
```json
{
  "contract_id": "abc123-def456-ghi789",
  "filename": "contract.pdf",
  "status": "completed",
  "score": 85,
  "extracted_data": {
    "parties": [
      {"name": "TechCorp Inc.", "role": "Service Provider", "confidence": 95}
    ],
    "financial_details": {
      "total_value": "$150,000",
      "currency": "USD"
    }
  },
  "gaps": [
    {"field": "SLA Terms", "importance": "Medium", "status": "Missing"}
  ],
  "confidence_scores": {
    "parties": 95.0,
    "financial_details": 88.5
  }
}
```

## Data Extraction

The system extracts and structures the following contract information:

### Party Identification (25 points)
- Contract parties with roles (client, vendor, service provider)
- Legal entity names and types
- Authorized signatories

### Financial Details (30 points)
- Total contract value and currency
- Line items with descriptions, quantities, and prices
- Tax information and rates

### Payment Structure (20 points)
- Payment terms (Net 30, Net 60, etc.)
- Payment schedules and methods
- Banking details

### Service Level Agreements (15 points)
- Response time requirements
- Uptime guarantees
- Penalty clauses

### Contact Information (10 points)
- Billing and technical contacts
- Email addresses and phone numbers

### Additional Information
- Account numbers and references
- Revenue classification (recurring vs one-time)
- Renewal terms and conditions

## Scoring Algorithm

The system uses a weighted scoring approach:

- **Financial Completeness**: 30% of total score
- **Party Identification**: 25% of total score
- **Payment Terms**: 20% of total score
- **SLA Definition**: 15% of total score
- **Contact Information**: 10% of total score

Each section is evaluated based on:
- Data completeness
- Extraction confidence
- Field importance

## Configuration

### Environment Variables

```bash
# Database
MONGO_URI=mongodb://localhost:27017/contract_db

# Task Queue
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Application
SECRET_KEY=your-secret-key-here
MAX_FILE_SIZE=52428800  # 50MB

# Optional
DEBUG=false
LOG_LEVEL=INFO
```

### File Limits

- **Maximum file size**: 50MB
- **Supported formats**: PDF only
- **File requirements**: Text-based PDFs (not scanned images)

## Testing

### Run all tests:
```bash
uv run test
```

### Run with coverage:
```bash
uv run test --cov-report=html
```

### Run specific test file:
```bash
uv run pytest tests/test_api.py -v
```

### Current test coverage:
- API endpoints: 90%+
- Extraction services: 85%+
- Core utilities: 95%+
- Overall coverage: ~90%

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
uv run format

# Lint code
uv run lint

# Type checking (if mypy is installed)
mypy src/
```

### Adding New Extraction Rules

1. Extend patterns in `src/services/extractor.py`
2. Update scoring weights in `src/core/config.py`
3. Add corresponding tests in `tests/test_extractor.py`

### Database Schema

Contracts are stored in MongoDB with the following structure:

```json
{
  "contract_id": "unique-identifier",
  "filename": "contract.pdf",
  "file_size": 2048576,
  "status": "completed",
  "progress": 100,
  "original_file": "<binary-data>",
  "extracted_data": { /* ... */ },
  "score": 85,
  "gaps": [ /* ... */ ],
  "confidence_scores": { /* ... */ },
  "upload_date": "2024-01-01T10:00:00",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:05:00"
}
```

## Performance Considerations

- **Concurrent Processing**: Celery workers handle multiple contracts simultaneously
- **Memory Management**: Large files are processed in chunks
- **Database Optimization**: Indexes on contract_id and status fields
- **File Storage**: Binary data stored in MongoDB (consider GridFS for >16MB files)

## Security

- **File Validation**: Strict PDF validation and size limits
- **Error Handling**: No sensitive information in error messages
- **CORS**: Configured for frontend origins only
- **Input Sanitization**: All inputs are validated and sanitized

## Monitoring and Logging

- **Health Checks**: `/api/v1/health` endpoint for service monitoring
- **Processing Statistics**: `/api/v1/contracts/stats` for analytics
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Error Tracking**: Comprehensive error logging and reporting

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**:
   - Check MongoDB is running: `docker ps` or `mongosh`
   - Verify connection string in `.env`

2. **Redis Connection Error**:
   - Check Redis is running: `redis-cli ping`
   - Verify Redis URL in `.env`

3. **Celery Worker Not Starting**:
   - Ensure Redis is accessible
   - Check for port conflicts
   - Review worker logs: `uv run celery --loglevel=debug`

4. **PDF Extraction Fails**:
   - Ensure PDF is text-based (not scanned image)
   - Check file size limits
   - Verify PDF is not password-protected

### Debug Mode

Enable debug mode by setting environment variables:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `uv run test`
5. Format code: `uv run format`
6. Submit pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the [troubleshooting section](#troubleshooting)
- Review [API documentation](http://localhost:8000/docs)
- Open an issue on GitHub

## Changelog

### v1.0.0
- Initial release
- Core contract extraction functionality
- RESTful API with full CRUD operations
- Async processing with Celery
- Comprehensive test suite
- Docker deployment support
