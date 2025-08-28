# Contract Intelligence Parser

A full-stack web application for automated contract analysis and data extraction using AI-powered document processing. Upload PDF contracts and get comprehensive insights including party information, financial details, payment terms, and automated scoring.

## 🚀 Features

### Backend (FastAPI)
- **PDF Processing**: Advanced PDF text extraction using pdfplumber
- **Async Processing**: Background contract parsing with Celery task queue
- **Data Extraction**: Comprehensive extraction of contract elements:
  - Party identification and roles
  - Financial details and line items
  - Payment terms and structure
  - Service Level Agreements (SLA)
  - Contact and account information
  - Revenue classification
- **Scoring System**: Weighted scoring algorithm (0-100 points) based on data completeness
- **Gap Analysis**: Identification of missing critical contract fields
- **RESTful API**: Complete CRUD operations for contract management
- **Real-time Status**: Track processing progress and status updates
- **File Management**: Secure file storage and download capabilities

### Frontend (React + TypeScript)
- **Modern UI**: Built with React, TypeScript, and Tailwind CSS
- **Drag & Drop Upload**: Intuitive file upload with progress tracking
- **Dashboard**: Contract overview with status indicators and statistics
- **Contract Details**: Comprehensive view of extracted contract data
- **Responsive Design**: Mobile-friendly interface with shadcn/ui components
- **Real-time Updates**: Live status updates using React Query
- **Data Visualization**: Charts and metrics for contract insights

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.13+)
- **Database**: MongoDB (with PyMongo)
- **Task Queue**: Celery with Redis broker
- **PDF Processing**: pdfplumber
- **Environment Management**: UV package manager
- **Testing**: pytest with coverage reporting
- **Containerization**: Docker and Docker Compose

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router
- **Icons**: Lucide React

## 📁 Project Structure

```
├── backend/                 # FastAPI backend application
│   ├── src/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Configuration and utilities
│   │   ├── database/       # MongoDB models and connection
│   │   ├── services/       # Business logic and extraction
│   │   ├── tasks/          # Celery async tasks
│   │   └── main.py         # FastAPI application entry point
│   ├── tests/              # Unit tests
│   ├── .env                # Environment variables
│   ├── pyproject.toml      # UV project configuration
│   ├── Dockerfile          # Container definition
│   └── docker-compose.yml  # Multi-service setup
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Application pages/routes
│   │   ├── services/       # API client and queries
│   │   ├── hooks/          # Custom React hooks
│   │   └── lib/            # Utility functions
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
└── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+** (for backend)
- **Node.js 18+** (for frontend)
- **UV Package Manager** (for Python dependency management)
- **MongoDB** (local installation or cloud instance)
- **Redis** (local installation or cloud instance)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Technical_Assignment_Contract_Intelligence/backend
   ```

2. **Install dependencies using UV**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB and Redis configurations
   ```

4. **Run with Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```

5. **Or run locally**
   ```bash
   # Start MongoDB and Redis services locally
   
   # Run the FastAPI application
   uv run uvicorn src.main:app --reload
   
   # In a separate terminal, start Celery worker
   uv run celery -A src.tasks.celery worker --loglevel=info
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   bun install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Configure API_BASE_URL if different from default
   ```

4. **Start development server**
   ```bash
   npm run dev
   # or
   bun run dev
   ```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
MONGO_URI=mongodb://localhost:27017/contract_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
SECRET_KEY=your-secret-key
MAX_FILE_SIZE=52428800  # 50MB
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 📚 API Documentation

The backend provides comprehensive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/contracts/upload` - Upload contract PDF
- `GET /api/v1/contracts` - List all contracts
- `GET /api/v1/contracts/{id}` - Get contract details
- `DELETE /api/v1/contracts/{id}` - Delete contract
- `GET /api/v1/contracts/{id}/download` - Download original PDF
- `GET /api/v1/stats` - Get contract statistics
- `GET /api/v1/health` - Health check

## 🧪 Testing

### Backend Tests
```bash
cd backend
uv run pytest tests/ -v --cov=src
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🔍 Features in Detail

### Contract Data Extraction
The system extracts and structures the following information from uploaded contracts:

- **Parties**: Contractor, client, vendor information
- **Financial Data**: Contract values, line items, pricing
- **Payment Terms**: Net days, payment schedules
- **Contact Information**: Names, emails, phone numbers
- **Account Details**: Account numbers, banking information
- **Dates**: Contract dates, expiration, renewal terms
- **Service Levels**: SLA requirements and metrics

### Scoring Algorithm
Contracts are scored on a 0-100 scale based on:
- Data completeness (40%)
- Critical field presence (30%)
- Data quality and formatting (20%)
- Additional metadata (10%)

### Gap Analysis
The system identifies missing critical fields and suggests improvements for better contract completeness.

## 🚢 Deployment

### Docker Deployment
```bash
# Backend with all services
cd backend
docker-compose up -d

# Frontend
cd frontend
docker build -t contract-frontend .
docker run -p 3000:80 contract-frontend
```

### Production Considerations
- Use environment-specific configuration files
- Enable HTTPS with proper SSL certificates
- Configure MongoDB and Redis for production workloads
- Set up proper logging and monitoring
- Implement backup strategies for contract data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🗺️ Roadmap

- [ ] Integration with more document formats (Word, Excel)
- [ ] Advanced AI/ML models for better extraction accuracy
- [ ] Template-based contract generation
- [ ] Integration with external legal databases
- [ ] Advanced analytics and reporting features
- [ ] Multi-language contract support