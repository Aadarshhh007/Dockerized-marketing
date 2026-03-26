# Marketing Service

A fully containerized Python marketing campaign management service with a complete DevOps pipeline.

## Stack
- **Backend**: Python FastAPI
- **Frontend**: Python Streamlit
- **Database**: PostgreSQL
- **Container**: Docker (multi-stage builds)
- **Orchestration**: Docker Compose (local) / Kubernetes on AWS EKS (production)
- **CI/CD**: GitHub Actions → AWS ECR → AWS EKS

---

## Quick Start (Local with Docker Compose)

```bash
cd marketing-service
docker compose up -d
```

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:8501        |
| Backend   | http://localhost:8000/docs   |
| Via Nginx | http://localhost (port 80)   |

---

## Project Structure

```
marketing-service/
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── models.py         # Pydantic models
│   │   ├── routes.py         # API endpoints
│   │   └── database.py       # In-memory data layer
│   ├── tests/                # Pytest test suite
│   ├── main.py               # FastAPI entrypoint
│   ├── requirements.txt
│   └── Dockerfile            # Multi-stage build
├── frontend/                 # Streamlit dashboard
│   ├── app.py                # Streamlit pages
│   ├── requirements.txt
│   └── Dockerfile            # Multi-stage build
├── k8s/                      # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── hpa.yaml              # Horizontal Pod Autoscaler
│   └── ingress.yaml          # AWS ALB Ingress
├── nginx/
│   └── nginx.conf            # Reverse proxy config
├── .github/workflows/
│   └── ci-cd.yml             # GitHub Actions pipeline
└── docker-compose.yml
```

---

## CI/CD Pipeline (GitHub Actions)

### Required GitHub Secrets

| Secret                 | Description                          |
|------------------------|--------------------------------------|
| `AWS_ACCESS_KEY_ID`    | IAM user access key                  |
| `AWS_SECRET_ACCESS_KEY`| IAM user secret key                  |
| `AWS_ACCOUNT_ID`       | 12-digit AWS account ID              |

### Pipeline Stages

```
Code Push → GitHub
     │
     ▼
┌─────────────────┐
│ Job 1: Test     │  Lint (Ruff + Black) + Pytest
└────────┬────────┘
         │ on success
         ▼
┌─────────────────┐
│ Job 2: Build    │  Multi-stage Docker build
│   & Push        │  Push to AWS ECR (backend + frontend)
└────────┬────────┘
         │ on main branch only
         ▼
┌─────────────────┐
│ Job 3: Deploy   │  Update EKS via kubectl
│   to EKS        │  Rolling update → zero downtime
└─────────────────┘
```

---

## AWS Setup

### 1. Create ECR Repositories

```bash
aws ecr create-repository --repository-name marketing-backend  --region us-east-1
aws ecr create-repository --repository-name marketing-frontend --region us-east-1
```

### 2. Create EKS Cluster

```bash
eksctl create cluster \
  --name marketing-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 4 \
  --managed
```

### 3. IAM Policy for GitHub Actions

Attach the following policies to your GitHub Actions IAM user:
- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonEKSClusterPolicy`
- `AmazonEKSWorkerNodePolicy`

---

## Kubernetes Deployment (Manual)

```bash
# Configure kubectl
aws eks update-kubeconfig --name marketing-cluster --region us-east-1

# Deploy all manifests
kubectl apply -f k8s/

# Watch pods
kubectl get pods -n marketing -w

# Check services
kubectl get svc -n marketing

# Check ingress (ALB URL)
kubectl get ingress -n marketing
```

---

## API Endpoints

| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/api/v1/health`          | Health check             |
| GET    | `/api/v1/campaigns`       | List all campaigns       |
| POST   | `/api/v1/campaigns`       | Create a campaign        |
| GET    | `/api/v1/campaigns/{id}`  | Get a campaign by ID     |
| PUT    | `/api/v1/campaigns/{id}`  | Update a campaign        |
| DELETE | `/api/v1/campaigns/{id}`  | Delete a campaign        |
| GET    | `/api/v1/users`           | List all users           |
| POST   | `/api/v1/users`           | Create a user            |
| GET    | `/api/v1/stats`           | Campaign analytics stats |

Interactive docs: `http://localhost:8000/docs`

---

## Resume Summary

> "Built a Python-based Marketing Service using FastAPI (backend) and Streamlit (frontend) with multi-stage Docker builds and Docker Compose for local orchestration. Designed a CI/CD pipeline using GitHub Actions to automate linting, testing, and deployment. Pushed Docker images to AWS ECR and deployed scalable containers on AWS EKS orchestrated with Kubernetes, featuring auto-scaling via HPA and zero-downtime rolling updates."
