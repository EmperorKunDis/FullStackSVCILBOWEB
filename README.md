# Bannerlord Full Stack Web Application

A comprehensive web application for Mount & Blade II: Bannerlord, featuring an immersive 3D interface, Python backend, and containerized deployment. This application provides a modern way to interact with Bannerlord content through a sophisticated web interface.

## 🏗️ Architecture Overview

The project follows a modern microservices architecture with three main components:

1. **Frontend (React + Three.js)**
   - Modern React application with 3D capabilities
   - Interactive 3D user interface
   - Responsive design with TailwindCSS

2. **Backend (Python)**
   - RESTful API service
   - Game data processing and management
   - Environment-based configuration

3. **Nginx (Reverse Proxy)**
   - Request routing and load balancing
   - Static content serving
   - SSL/TLS termination

## 🚀 Technologies

### Frontend
- React 18
- Three.js & React Three Fiber
- TailwindCSS
- Vite
- ESLint

### Backend
- Python
- Flask/FastAPI
- SQLAlchemy
- Environment-based configuration

### Infrastructure
- Docker & Docker Compose
- Nginx
- Environment variable management
- Development and production configurations

## 📦 Prerequisites

- Docker and Docker Compose
- Node.js (for local frontend development)
- Python 3.8+ (for local backend development)
- Git

## 🛠️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone [your-repository-url]
   cd BannerlordFullStackWebApp
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- Nginx (Main Entry): http://localhost:8000

## 📁 Project Structure

```
BannerlordFullStackWebApp/
├── frontend/                 # React frontend application
│   ├── public/              # Static assets
│   │   └── models/         # 3D models
│   ├── src/                # Source code
│   └── package.json        # Frontend dependencies
├── backend/                 # Python backend service
│   ├── src/               # Backend source code
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile        # Backend container config
├── nginx/                   # Nginx configuration
│   └── nginx.conf         # Nginx routing rules
├── compose.yaml            # Docker Compose configuration
├── .env                    # Environment variables
└── README.md              # Project documentation
```

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python src/server.py
```

### Docker Development
```bash
# Build and start all services
docker-compose up --build

# Rebuild specific service
docker-compose up -d --build [service-name]

# View logs
docker-compose logs -f [service-name]
```

## 🔨 Configuration

### Environment Variables
- `DEBUG`: Enable debug mode (true/false)
- `NODE_ENV`: Node.js environment (development/production)
- Additional environment variables as needed

### Nginx Configuration
- Located in `nginx/nginx.conf`
- Configures routing and load balancing
- Handles static file serving

## 🚀 Deployment

1. **Production Build**
   ```bash
   # Frontend production build
   cd frontend && npm run build

   # Start production services
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Environment Configuration**
   - Update `.env` with production values
   - Configure SSL certificates
   - Set up proper security measures

3. **Monitoring**
   - Set up logging
   - Configure health checks
   - Monitor system resources

## 🧪 Testing

### Frontend Testing
```bash
cd frontend
npm run test
```

### Backend Testing
```bash
cd backend
python -m pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

MIT License

## 🌟 Acknowledgments

- Mount & Blade II: Bannerlord team for inspiration
- Three.js community for 3D web capabilities
- Open source community for various tools and libraries
