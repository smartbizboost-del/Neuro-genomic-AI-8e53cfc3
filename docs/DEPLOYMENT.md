# Deployment Guide

This document explains how to deploy Neuro-Genomic AI using the provided GitHub Actions workflows and Kubernetes manifests.

1) Local quick deploy (developer machine)

```bash
# Build and start with docker-compose
docker-compose up -d --build

# Or use helper script (requires Docker)
./scripts/deploy_local.sh
```

2) GitHub Actions automated deploy

- Add repository secret `KUBE_CONFIG` containing your kubeconfig file base64-encoded.
- The workflow `.github/workflows/deploy-k8s.yml` will:
  - build images and push to GitHub Container Registry (GHCR)
  - apply manifests under `infrastructure/kubernetes`
  - update deployment images to point at GHCR tags

3) Kubernetes cluster requirements

- Create the `neuro-genomic` namespace: `kubectl apply -f infrastructure/kubernetes/namespace.yaml`
- Create `neuro-secrets` with real values (see `neuro-secrets-template.yaml`) or use an external secret manager.

Example to create the secret from environment variables:

```bash
kubectl create secret generic neuro-secrets \
  --namespace neuro-genomic \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=redis-url="$REDIS_URL" \
  --from-literal=minio-endpoint="$MINIO_ENDPOINT" \
  --from-literal=minio-access-key="$MINIO_ACCESS_KEY" \
  --from-literal=minio-secret-key="$MINIO_SECRET_KEY"
```

4) Notes

- Ensure the `neuro-secrets` secret keys match the environment variables referenced in `infrastructure/kubernetes/deployment.yaml`.
- The deploy workflow expects the cluster to already have the namespace and RBAC to accept `kubectl apply` via the provided kubeconfig.
