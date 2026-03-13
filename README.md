# Django Git Playground

A robust Django project configured for both local development and production environments. It features a complete Docker setup, PostgreSQL integration, automated testing, and a full CI/CD pipeline using GitHub Actions for deployment to AWS EC2.

---

## 📝 Features

- **Django Backend:** Powered by Django and Django REST Framework.
- **Database:** PostgreSQL integration via psycopg2.
- **Dockerized Environments:** Built-in Docker configurations for local development and optimized `production` setups.
- **Testing:** Configured with `pytest` for streamlined unit and integration testing.
- **CI/CD Pipeline:** Fully automated GitHub Actions workflow for building, testing, pushing Docker images to Docker Hub, and deploying via SSH to an EC2 instance.
- **Code Quality:** Pre-configured with Black and isort formatting tools.

---

## ⚙️ Prerequisites

- Docker >= 24.x
- Docker Compose >= 2.x
- Git
- Python 3.12 (for optional local development outside Docker)

---

## 📂 Project Structure

```text
django-git-playground/
├── apps/                  # Django applications (e.g., authentication)
├── devops/                # Docker, Compose and infrastructure configurations
│   ├── local/             # Local development environment configs
│   └── production/        # Production environment Dockerfiles and configs
├── django_server/         # Core Django project settings and routing
├── .github/workflows/     # GitHub Actions CI/CD workflows
├── manage.py              # Django CLI management script
├── pytest.ini             # Pytest configuration
├── requirements.txt       # Project-wide Python dependencies
└── .env.example           # Example environment variables template
```

---

## 🐳 Local Development (Docker Setup)

### 1. Environment Configuration
Copy the sample environment file to `.env`:
```bash
cp .env.example .env
```
Update `.env` with intended ports and credentials. For the local Docker stack, `DB_HOST` should match the database service name in `docker-compose.yaml` (usually `postgres-db`).

### 2. Build & Run Containers
Assuming the local docker-compose configuration resides in the devops directory (or root, check your specific path format):
```bash
docker compose -f devops/docker-compose.yaml --env-file .env up -d --build
```
This will:
- Build the Django backend image.
- Initialize the PostgreSQL database container.
- Start the Django server and sync volumes for live-code hot-reloading.

### 3. Verify Containers Are Running
```bash
docker ps
```
You should see your Django backend server and PostgreSQL database containers mapped appropriately.

### 4. Running Backend Commands
To execute standard Django management duties (migrations, creating superusers) inside the running cluster container:
```bash
docker compose exec backend-server python manage.py migrate
docker compose exec backend-server python manage.py createsuperuser
docker compose exec backend-server python manage.py collectstatic
```

### 5. Testing
The application uses pytest. Easily run your whole test suite directly inside the development container:
```bash
docker compose exec backend-server pytest -v
```

### 6. Reset or Teardown
To spin down containers and remove associated volumes (useful to reset database states):
```bash
docker compose -f devops/local/docker-compose.yaml down -v
```

---

## 🚀 CI/CD and Production Deployment

The project employs a robust Continuous Deployment pipeline modeled natively inside GitHub Actions (`.github/workflows/deploy.yml`).

### Workflow Outline:
1. **Build and Test:** Push code to `main`. Actions automatically check out code, setup Python, install dependencies, and run `pytest`. The deploy stops here if tests fail.
2. **Publish Docker Images:** An optimized production Docker Image is natively built and pushed securely spanning your Docker Hub container registry.
3. **Deploy safely to EC2 via SSH:** Safe propagation sends docker configs/updates securely to the EC2 server (`~/config`) via SCP. It then runs an encapsulated SSH script that handles injecting secure Action secrets as `.env` variables, cleanly tearing down old containers via `docker-compose down`, syncing the newly tagged Docker image, and launching application containers back to life with zero orphaned instances.

**Production Mechanics:** 
Deployments inherently rely heavily on `Gunicorn` handling the traffic WSGI gateways with static files rendered reliably through Whitenoise or Nginx dependencies defined in `devops/production`. 

---

## 🌐 Accessing the App

With localized Docker systems operating correctly:
- **Django Application Root:** [http://localhost:8000](http://localhost:8000)
- **Django Admin Interface:** [http://localhost:8000/admin](http://localhost:8000/admin)
