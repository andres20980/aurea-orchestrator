# Kubernetes Deployment Quick Start Guide

This guide provides quick steps to deploy the Aurea Orchestrator to Kubernetes.

## Prerequisites Checklist

- [ ] Kubernetes cluster (v1.20+) with kubectl configured
- [ ] kustomize v4.0+ installed (or use `kubectl apply -k`)
- [ ] KEDA operator installed in the cluster
- [ ] Metrics Server installed (for HPA)
- [ ] (Optional) NGINX Ingress Controller
- [ ] (Optional) cert-manager for TLS
- [ ] (Optional) Prometheus Adapter for custom metrics

## Quick Install Prerequisites

### Install KEDA
```bash
kubectl apply -f https://github.com/kedacore/keda/releases/download/v2.12.0/keda-2.12.0.yaml
```

### Install Metrics Server
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Install NGINX Ingress (Optional)
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml
```

### Install cert-manager (Optional)
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

## Deployment Steps

### 1. Configure Secrets

**IMPORTANT:** Update the secrets before deploying!

Edit `k8s/base/secret.yaml` and replace placeholder values:
```bash
# Option 1: Edit the file directly
vim k8s/base/secret.yaml

# Option 2: Create secret separately
kubectl create secret generic aurea-orchestrator-secret \
  --from-literal=DB_USER=your-db-user \
  --from-literal=DB_PASSWORD=your-db-password \
  --from-literal=REDIS_PASSWORD=your-redis-password \
  --from-literal=SECRET_KEY=your-secret-key \
  --from-literal=JWT_SECRET=your-jwt-secret \
  -n aurea-orchestrator --dry-run=client -o yaml > k8s/base/secret.yaml
```

### 2. Update Configuration

Edit configuration in `k8s/base/configmap.yaml` if needed:
- Database host/port
- Redis host/port
- API configuration
- Worker settings

### 3. Configure Ingress

Update the hostname in:
- `k8s/overlays/dev/ingress-patch.yaml` - for development
- `k8s/overlays/prod/ingress-patch.yaml` - for production

Replace `dev.aurea-orchestrator.example.com` and `aurea-orchestrator.example.com` with your actual domains.

### 4. Build and Push Images

Build your Docker images and push to a registry:

```bash
# Build images
docker build -t your-registry.io/aurea-orchestrator-api:dev -f Dockerfile.api .
docker build -t your-registry.io/aurea-orchestrator-worker:dev -f Dockerfile.worker .

# Push images
docker push your-registry.io/aurea-orchestrator-api:dev
docker push your-registry.io/aurea-orchestrator-worker:dev
```

Update image names in overlay kustomization files:
```yaml
images:
  - name: aurea-orchestrator-api
    newName: your-registry.io/aurea-orchestrator-api
    newTag: dev
```

### 5. Deploy to Development

```bash
# Preview what will be deployed
kubectl kustomize k8s/overlays/dev

# Apply the manifests
kubectl apply -k k8s/overlays/dev

# Wait for deployment
kubectl rollout status deployment/dev-aurea-api -n aurea-orchestrator-dev
kubectl rollout status deployment/dev-aurea-celery-worker -n aurea-orchestrator-dev
```

### 6. Verify Deployment

```bash
# Check all resources
kubectl get all -n aurea-orchestrator-dev

# Check pods
kubectl get pods -n aurea-orchestrator-dev

# Check services
kubectl get svc -n aurea-orchestrator-dev

# Check ingress
kubectl get ingress -n aurea-orchestrator-dev

# Check HPA
kubectl get hpa -n aurea-orchestrator-dev

# Check KEDA ScaledObjects
kubectl get scaledobject -n aurea-orchestrator-dev
```

### 7. View Logs

```bash
# API logs
kubectl logs -f -l app.kubernetes.io/component=api -n aurea-orchestrator-dev

# Worker logs
kubectl logs -f -l app.kubernetes.io/component=worker -n aurea-orchestrator-dev
```

### 8. Run Database Migration

```bash
# Apply the migration job
kubectl apply -f k8s/base/db-migration-job.yaml -n aurea-orchestrator-dev

# Watch the migration
kubectl logs -f job/dev-aurea-db-migration -n aurea-orchestrator-dev

# Check job status
kubectl get jobs -n aurea-orchestrator-dev
```

## Deploy to Production

For production deployment, follow the same steps but use the `prod` overlay:

```bash
# Update production secrets
# Edit k8s/base/secret.yaml with production values

# Build and push production images with 'stable' tag
docker build -t your-registry.io/aurea-orchestrator-api:stable -f Dockerfile.api .
docker push your-registry.io/aurea-orchestrator-api:stable

# Preview production manifests
kubectl kustomize k8s/overlays/prod

# Deploy to production
kubectl apply -k k8s/overlays/prod

# Monitor deployment
kubectl rollout status deployment/prod-aurea-api -n aurea-orchestrator-prod
kubectl rollout status deployment/prod-aurea-celery-worker -n aurea-orchestrator-prod
```

## Accessing the Application

### Development
```bash
# Port-forward to access locally
kubectl port-forward svc/dev-aurea-api-service 8000:80 -n aurea-orchestrator-dev

# Access at http://localhost:8000
```

### Production
Access via the configured ingress hostname:
- https://aurea-orchestrator.example.com

## Monitoring

### Check Autoscaling
```bash
# HPA status
kubectl describe hpa dev-aurea-api-hpa -n aurea-orchestrator-dev

# KEDA ScaledObject status
kubectl describe scaledobject dev-aurea-celery-worker-scaler -n aurea-orchestrator-dev

# Watch pod count changes
watch kubectl get pods -n aurea-orchestrator-dev
```

### Check Metrics
```bash
# CPU/Memory usage
kubectl top pods -n aurea-orchestrator-dev

# Get events
kubectl get events -n aurea-orchestrator-dev --sort-by='.lastTimestamp'
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n aurea-orchestrator-dev
kubectl logs <pod-name> -n aurea-orchestrator-dev
```

### Check HPA
```bash
kubectl describe hpa dev-aurea-api-hpa -n aurea-orchestrator-dev
kubectl get hpa -n aurea-orchestrator-dev -w
```

### Check KEDA
```bash
kubectl logs -n keda -l app=keda-operator
kubectl describe scaledobject dev-aurea-celery-worker-scaler -n aurea-orchestrator-dev
```

### View all events
```bash
kubectl get events -n aurea-orchestrator-dev --sort-by='.lastTimestamp' | tail -20
```

## Cleanup

### Remove development deployment
```bash
kubectl delete -k k8s/overlays/dev
```

### Remove production deployment
```bash
kubectl delete -k k8s/overlays/prod
```

## Next Steps

1. Set up CI/CD pipeline to automate deployments
2. Configure external secrets management (Vault, AWS Secrets Manager, etc.)
3. Set up monitoring with Prometheus and Grafana
4. Configure log aggregation (ELK, Loki, etc.)
5. Set up alerting for critical metrics
6. Implement backup and disaster recovery procedures
7. Configure network policies for enhanced security
8. Set up service mesh (optional, e.g., Istio, Linkerd)

## Resources

- Full documentation: `k8s/README.md`
- Kustomize docs: https://kustomize.io/
- KEDA docs: https://keda.sh/
- Kubernetes docs: https://kubernetes.io/docs/
