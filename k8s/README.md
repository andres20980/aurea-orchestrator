# Kubernetes Manifests for Aurea Orchestrator

This directory contains Kubernetes manifests for deploying the Aurea Orchestrator application, including API service and Celery workers.

## Directory Structure

```
k8s/
├── base/                           # Base Kubernetes manifests
│   ├── namespace.yaml             # Namespace definition
│   ├── priority-class.yaml        # PriorityClass for pod scheduling
│   ├── serviceaccount.yaml        # ServiceAccount for pods
│   ├── configmap.yaml             # Application configuration
│   ├── secret.yaml                # Secret configuration (passwords, keys)
│   ├── api-deployment.yaml        # API deployment with probes
│   ├── worker-deployment.yaml     # Celery worker deployment with probes
│   ├── api-service.yaml           # Service for API
│   ├── ingress.yaml               # Ingress configuration
│   ├── api-hpa.yaml               # HPA for API (CPU/RPS based)
│   ├── worker-keda-scaledobject.yaml  # KEDA ScaledObject for workers
│   ├── poddisruptionbudget.yaml   # PDBs for high availability
│   ├── db-migration-job.yaml      # Database migration job
│   └── kustomization.yaml         # Base kustomization
├── overlays/
│   ├── dev/                       # Development environment overlay
│   │   ├── kustomization.yaml
│   │   ├── api-deployment-patch.yaml
│   │   ├── worker-deployment-patch.yaml
│   │   ├── configmap-patch.yaml
│   │   └── ingress-patch.yaml
│   └── prod/                      # Production environment overlay
│       ├── kustomization.yaml
│       ├── api-deployment-patch.yaml
│       ├── worker-deployment-patch.yaml
│       ├── configmap-patch.yaml
│       ├── ingress-patch.yaml
│       ├── api-hpa-patch.yaml
│       └── worker-keda-patch.yaml
└── README.md                      # This file
```

## Features

### 1. Deployments
- **API Deployment**: Runs the REST API server with:
  - Liveness probe at `/health/live`
  - Readiness probe at `/health/ready`
  - Prometheus scrape annotations
  - Security context (non-root, read-only filesystem)
  - Pod anti-affinity for high availability

- **Celery Worker Deployment**: Runs background task workers with:
  - Celery-specific liveness/readiness probes
  - Prometheus metrics export
  - Security hardening
  - Pod anti-affinity

### 2. Services
- **API Service**: ClusterIP service exposing the API on port 80

### 3. Ingress
- NGINX Ingress Controller configuration
- TLS/SSL termination with cert-manager
- Rate limiting
- Configurable hostname per environment

### 4. ConfigMaps and Secrets
- **ConfigMap**: Non-sensitive configuration (log levels, worker counts, service endpoints)
- **Secret**: Sensitive data (database credentials, API keys, passwords)

### 5. Autoscaling

#### HPA (Horizontal Pod Autoscaler) for API
- Scales based on:
  - CPU utilization (70%)
  - Memory utilization (80%)
  - HTTP requests per second (100 RPS average)
- Min replicas: 2 (dev: 1, prod: 3)
- Max replicas: 10 (dev: 5, prod: 20)
- Advanced scaling behavior for gradual scale-up/down

#### KEDA ScaledObject for Workers
- Scales based on:
  - Redis queue length (Celery tasks)
  - CPU utilization
  - Memory utilization
- Min replicas: 2 (dev: 1, prod: 3)
- Max replicas: 20 (dev: 10, prod: 50)
- Polling interval: 30s
- Cooldown period: 5 minutes

### 6. High Availability

#### PodDisruptionBudgets
- Ensures minimum 1 pod is always available during voluntary disruptions
- Separate PDBs for API and worker deployments

#### PriorityClasses
- `aurea-high-priority` (1000): For critical API pods
- `aurea-normal-priority` (500): For worker pods

### 7. Observability

#### Prometheus Integration
- Scrape annotations on all deployments
- Metrics exposed for monitoring
- Custom metrics for HPA (RPS)

### 8. Database Migrations
- Pre-deployment job for running database migrations
- Configured as Helm hook (if using Helm)
- TTL for automatic cleanup after completion

## Prerequisites

1. **Kubernetes Cluster**: v1.20 or later
2. **kubectl**: Configured to access your cluster
3. **kustomize**: v4.0 or later (or use `kubectl apply -k`)
4. **KEDA**: Install KEDA operator for worker autoscaling
   ```bash
   kubectl apply -f https://github.com/kedacore/keda/releases/download/v2.12.0/keda-2.12.0.yaml
   ```
5. **Metrics Server**: For HPA to work
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```
6. **NGINX Ingress Controller**: (Optional) For ingress
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml
   ```
7. **cert-manager**: (Optional) For TLS certificates
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```
8. **Prometheus Adapter**: (Optional) For custom metrics (RPS)
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install prometheus-adapter prometheus-community/prometheus-adapter
   ```

## Deployment

### Deploy to Development

1. **Update secrets** in `k8s/base/secret.yaml` with actual values
2. **Build and push images** with `dev` tag
3. **Deploy using kustomize**:
   ```bash
   kubectl apply -k k8s/overlays/dev
   ```

### Deploy to Production

1. **Update secrets** in `k8s/base/secret.yaml` with production values
2. **Build and push images** with `stable` tag
3. **Deploy using kustomize**:
   ```bash
   kubectl apply -k k8s/overlays/prod
   ```

### Run Database Migration

```bash
kubectl apply -f k8s/base/db-migration-job.yaml
kubectl logs -f job/aurea-db-migration -n aurea-orchestrator
```

## Configuration

### Environment-Specific Configuration

Edit the overlay files to customize for each environment:
- **Dev**: `k8s/overlays/dev/*-patch.yaml`
- **Prod**: `k8s/overlays/prod/*-patch.yaml`

### Secrets Management

⚠️ **Important**: Never commit real secrets to version control!

Options for managing secrets:
1. **Sealed Secrets**: Use bitnami-labs/sealed-secrets
2. **External Secrets Operator**: Integrate with AWS Secrets Manager, GCP Secret Manager, etc.
3. **Vault**: Use HashiCorp Vault
4. **Manual**: Apply secrets separately using `kubectl create secret`

Example using kubectl:
```bash
kubectl create secret generic aurea-orchestrator-secret \
  --from-literal=DB_PASSWORD=your-password \
  --from-literal=SECRET_KEY=your-secret-key \
  -n aurea-orchestrator
```

### Image Configuration

Update image tags in overlay kustomization files:
```yaml
images:
  - name: aurea-orchestrator-api
    newName: your-registry.io/aurea-orchestrator-api
    newTag: v1.0.0
```

## Monitoring

### Check Deployment Status
```bash
kubectl get deployments -n aurea-orchestrator
kubectl get pods -n aurea-orchestrator
kubectl get hpa -n aurea-orchestrator
kubectl get scaledobject -n aurea-orchestrator
```

### View Logs
```bash
# API logs
kubectl logs -f deployment/aurea-api -n aurea-orchestrator

# Worker logs
kubectl logs -f deployment/aurea-celery-worker -n aurea-orchestrator
```

### Check Autoscaling
```bash
# HPA status
kubectl describe hpa aurea-api-hpa -n aurea-orchestrator

# KEDA status
kubectl describe scaledobject aurea-celery-worker-scaler -n aurea-orchestrator
```

### Prometheus Metrics
Access metrics endpoints:
```bash
# Port-forward to API
kubectl port-forward svc/aurea-api-service 8000:80 -n aurea-orchestrator
curl http://localhost:8000/metrics
```

## Scaling

### Manual Scaling
```bash
# Scale API
kubectl scale deployment aurea-api --replicas=5 -n aurea-orchestrator

# Scale Workers
kubectl scale deployment aurea-celery-worker --replicas=10 -n aurea-orchestrator
```

### Autoscaling Adjustment

Edit HPA for API:
```bash
kubectl edit hpa aurea-api-hpa -n aurea-orchestrator
```

Edit KEDA ScaledObject for workers:
```bash
kubectl edit scaledobject aurea-celery-worker-scaler -n aurea-orchestrator
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n aurea-orchestrator
kubectl logs <pod-name> -n aurea-orchestrator
```

### HPA not scaling
```bash
# Check metrics server
kubectl get apiservice v1beta1.metrics.k8s.io -o yaml

# Check HPA status
kubectl describe hpa aurea-api-hpa -n aurea-orchestrator
```

### KEDA not scaling workers
```bash
# Check KEDA operator logs
kubectl logs -n keda -l app=keda-operator

# Check ScaledObject
kubectl describe scaledobject aurea-celery-worker-scaler -n aurea-orchestrator
```

### Ingress not working
```bash
# Check ingress
kubectl describe ingress aurea-api-ingress -n aurea-orchestrator

# Check ingress controller
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

## Cleanup

### Remove dev deployment
```bash
kubectl delete -k k8s/overlays/dev
```

### Remove prod deployment
```bash
kubectl delete -k k8s/overlays/prod
```

### Remove base resources
```bash
kubectl delete -k k8s/base
```

## Best Practices

1. **Always use kustomize overlays** for environment-specific configuration
2. **Use external secrets management** for production
3. **Set resource requests and limits** for all containers
4. **Enable security context** with non-root users
5. **Use liveness and readiness probes** for all deployments
6. **Configure PodDisruptionBudgets** for high availability
7. **Monitor and adjust autoscaling** based on actual load
8. **Use pod anti-affinity** to spread pods across nodes
9. **Tag images properly** and never use `latest` in production
10. **Run database migrations** before deploying new versions

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [KEDA Documentation](https://keda.sh/)
- [HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)
