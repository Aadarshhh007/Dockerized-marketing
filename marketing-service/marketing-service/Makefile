# ============================================================
# Marketing Service — Makefile
# Usage: make <target>
# ============================================================

.PHONY: help build up down restart logs test lint format clean \
        push-ecr deploy-k8s rollout-status k8s-logs k8s-delete \
        backend-shell frontend-shell db-shell

AWS_REGION     ?= us-east-1
AWS_ACCOUNT_ID ?= $(shell aws sts get-caller-identity --query Account --output text 2>/dev/null)
ECR_REGISTRY   ?= $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
IMAGE_TAG      ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")
EKS_CLUSTER    ?= marketing-cluster
K8S_NAMESPACE  ?= marketing

# ──────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────
help:
	@echo ""
	@echo "  Marketing Service — Available Commands"
	@echo "  ─────────────────────────────────────"
	@echo "  Local Development"
	@echo "    make build          Build all Docker images"
	@echo "    make up             Start all services (detached)"
	@echo "    make down           Stop and remove containers"
	@echo "    make restart        Restart all services"
	@echo "    make logs           Tail logs from all containers"
	@echo "    make backend-shell  Open shell in backend container"
	@echo "    make frontend-shell Open shell in frontend container"
	@echo "    make db-shell       Open psql in postgres container"
	@echo ""
	@echo "  Testing & Quality"
	@echo "    make test           Run pytest test suite"
	@echo "    make lint           Run Ruff linter"
	@echo "    make format         Run Black formatter"
	@echo "    make clean          Remove __pycache__ and build artifacts"
	@echo ""
	@echo "  AWS / ECR"
	@echo "    make ecr-login      Authenticate Docker to AWS ECR"
	@echo "    make push-ecr       Build and push images to ECR"
	@echo ""
	@echo "  Kubernetes / EKS"
	@echo "    make kubeconfig     Update kubeconfig for EKS cluster"
	@echo "    make deploy-k8s     Apply all Kubernetes manifests"
	@echo "    make rollout-status Watch rollout status"
	@echo "    make k8s-logs       Stream backend pod logs"
	@echo "    make k8s-delete     Delete all K8s resources"
	@echo ""

# ──────────────────────────────────────────────
# Local Development
# ──────────────────────────────────────────────
build:
	docker compose build

up:
	docker compose up -d
	@echo ""
	@echo "  Services running:"
	@echo "    Frontend  → http://localhost:8501"
	@echo "    Backend   → http://localhost:8000/docs"
	@echo "    Via Nginx → http://localhost"
	@echo ""

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

backend-shell:
	docker compose exec backend /bin/bash

frontend-shell:
	docker compose exec frontend /bin/bash

db-shell:
	docker compose exec postgres psql -U marketing -d marketingdb

# ──────────────────────────────────────────────
# Testing & Quality
# ──────────────────────────────────────────────
test:
	@echo "Running tests..."
	cd backend && pip install -r requirements-dev.txt -q && pytest tests/ -v --tb=short

lint:
	@echo "Linting with Ruff..."
	cd backend && ruff check app/ main.py

format:
	@echo "Formatting with Black..."
	cd backend && black app/ main.py tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache"   -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	@echo "Cleaned."

# ──────────────────────────────────────────────
# AWS ECR
# ──────────────────────────────────────────────
ecr-login:
	aws ecr get-login-password --region $(AWS_REGION) \
	  | docker login --username AWS --password-stdin $(ECR_REGISTRY)

push-ecr: ecr-login
	@echo "Building and pushing backend ($(IMAGE_TAG))..."
	docker build -t $(ECR_REGISTRY)/marketing-backend:$(IMAGE_TAG) \
	             -t $(ECR_REGISTRY)/marketing-backend:latest \
	             --target production ./backend
	docker push $(ECR_REGISTRY)/marketing-backend:$(IMAGE_TAG)
	docker push $(ECR_REGISTRY)/marketing-backend:latest

	@echo "Building and pushing frontend ($(IMAGE_TAG))..."
	docker build -t $(ECR_REGISTRY)/marketing-frontend:$(IMAGE_TAG) \
	             -t $(ECR_REGISTRY)/marketing-frontend:latest \
	             --target production ./frontend
	docker push $(ECR_REGISTRY)/marketing-frontend:$(IMAGE_TAG)
	docker push $(ECR_REGISTRY)/marketing-frontend:latest

	@echo "Images pushed to ECR with tag: $(IMAGE_TAG)"

# ──────────────────────────────────────────────
# Kubernetes / EKS
# ──────────────────────────────────────────────
kubeconfig:
	aws eks update-kubeconfig --name $(EKS_CLUSTER) --region $(AWS_REGION)

deploy-k8s: kubeconfig
	@echo "Substituting image tag: $(IMAGE_TAG)"
	sed -i.bak "s|IMAGE_TAG|$(IMAGE_TAG)|g; s|ECR_REGISTRY|$(ECR_REGISTRY)|g" \
	    k8s/backend-deployment.yaml k8s/frontend-deployment.yaml
	kubectl apply -f k8s/ --namespace=$(K8S_NAMESPACE)
	@mv k8s/backend-deployment.yaml.bak  k8s/backend-deployment.yaml  2>/dev/null || true
	@mv k8s/frontend-deployment.yaml.bak k8s/frontend-deployment.yaml 2>/dev/null || true
	@echo "Deployment applied to namespace: $(K8S_NAMESPACE)"

rollout-status: kubeconfig
	kubectl rollout status deployment/marketing-backend  -n $(K8S_NAMESPACE)
	kubectl rollout status deployment/marketing-frontend -n $(K8S_NAMESPACE)
	kubectl get pods    -n $(K8S_NAMESPACE)
	kubectl get svc     -n $(K8S_NAMESPACE)
	kubectl get ingress -n $(K8S_NAMESPACE)

k8s-logs: kubeconfig
	kubectl logs -f deployment/marketing-backend -n $(K8S_NAMESPACE)

k8s-delete: kubeconfig
	kubectl delete -f k8s/ --namespace=$(K8S_NAMESPACE)
