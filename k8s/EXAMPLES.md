# Example Kustomization Customizations

This file contains examples of common customizations you might need.

## Custom Image Registry

To use your own container registry, update the `images` section in overlay kustomization files:

### Example: Using Docker Hub
```yaml
# k8s/overlays/dev/kustomization.yaml
images:
  - name: aurea-orchestrator-api
    newName: dockerhub-username/aurea-orchestrator-api
    newTag: dev-v1.0.0
  - name: aurea-orchestrator-worker
    newName: dockerhub-username/aurea-orchestrator-worker
    newTag: dev-v1.0.0
```

### Example: Using AWS ECR
```yaml
# k8s/overlays/prod/kustomization.yaml
images:
  - name: aurea-orchestrator-api
    newName: 123456789012.dkr.ecr.us-west-2.amazonaws.com/aurea-orchestrator-api
    newTag: prod-v1.0.0
  - name: aurea-orchestrator-worker
    newName: 123456789012.dkr.ecr.us-west-2.amazonaws.com/aurea-orchestrator-worker
    newTag: prod-v1.0.0
```

### Example: Using Google GCR
```yaml
images:
  - name: aurea-orchestrator-api
    newName: gcr.io/project-id/aurea-orchestrator-api
    newTag: v1.0.0
  - name: aurea-orchestrator-worker
    newName: gcr.io/project-id/aurea-orchestrator-worker
    newTag: v1.0.0
```

### Example: Using Azure ACR
```yaml
images:
  - name: aurea-orchestrator-api
    newName: myregistry.azurecr.io/aurea-orchestrator-api
    newTag: v1.0.0
  - name: aurea-orchestrator-worker
    newName: myregistry.azurecr.io/aurea-orchestrator-worker
    newTag: v1.0.0
```

## Custom Resource Limits

### Example: Smaller resource limits for cost savings
Create a new patch file `k8s/overlays/dev/resources-patch.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aurea-api
spec:
  template:
    spec:
      containers:
      - name: api
        resources:
          requests:
            cpu: 25m
            memory: 64Mi
          limits:
            cpu: 250m
            memory: 256Mi
```

Add to kustomization.yaml:
```yaml
patches:
  - path: resources-patch.yaml
```

### Example: Larger resource limits for high traffic
Create `k8s/overlays/prod/resources-high-traffic-patch.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aurea-api
spec:
  template:
    spec:
      containers:
      - name: api
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 4000m
            memory: 8Gi
```

## Custom Environment Variables

### Example: Adding custom environment variables
Create `k8s/overlays/prod/env-patch.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aurea-api
spec:
  template:
    spec:
      containers:
      - name: api
        env:
        - name: FEATURE_FLAG_NEW_UI
          value: "true"
        - name: SENTRY_DSN
          value: "https://xxx@sentry.io/xxx"
        - name: NEW_RELIC_LICENSE_KEY
          valueFrom:
            secretKeyRef:
              name: monitoring-secrets
              key: newrelic-license
```

## Custom Autoscaling

### Example: More aggressive HPA
Create `k8s/overlays/prod/aggressive-hpa-patch.yaml`:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: aurea-api-hpa
spec:
  minReplicas: 5
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 200
        periodSeconds: 15
```

### Example: Conservative KEDA scaling
Create `k8s/overlays/dev/conservative-keda-patch.yaml`:
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: aurea-celery-worker-scaler
spec:
  cooldownPeriod: 600
  triggers:
  - type: redis
    metadata:
      listLength: "20"
```

## Adding Image Pull Secrets

### Example: Add imagePullSecrets for private registry
Create `k8s/overlays/prod/imagepullsecrets-patch.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aurea-api
spec:
  template:
    spec:
      imagePullSecrets:
      - name: regcred
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aurea-celery-worker
spec:
  template:
    spec:
      imagePullSecrets:
      - name: regcred
```

Create the secret:
```bash
kubectl create secret docker-registry regcred \
  --docker-server=your-registry.io \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email \
  -n aurea-orchestrator-prod
```

## Custom Ingress Configuration

### Example: Adding WAF annotations (AWS ALB)
Create `k8s/overlays/prod/ingress-waf-patch.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: aurea-api-ingress
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/wafv2-acl-arn: arn:aws:wafv2:region:account:regional/webacl/name/id
    alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS-1-2-2017-01
```

### Example: Adding custom headers
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: aurea-api-ingress
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Frame-Options: DENY";
      more_set_headers "X-Content-Type-Options: nosniff";
      more_set_headers "X-XSS-Protection: 1; mode=block";
```

## Network Policies

### Example: Restricting network access
Create `k8s/base/networkpolicy.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aurea-api-netpol
  namespace: aurea-orchestrator
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/component: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

## Using External Secrets

### Example: Using External Secrets Operator
Create `k8s/base/externalsecret.yaml`:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: aurea-orchestrator-external-secret
  namespace: aurea-orchestrator
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: aurea-orchestrator-secret
    creationPolicy: Owner
  data:
  - secretKey: DB_PASSWORD
    remoteRef:
      key: aurea/db-password
  - secretKey: SECRET_KEY
    remoteRef:
      key: aurea/secret-key
  - secretKey: JWT_SECRET
    remoteRef:
      key: aurea/jwt-secret
```

## Adding Health Check Endpoints

### Example: Custom health check paths
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aurea-api
spec:
  template:
    spec:
      containers:
      - name: api
        livenessProbe:
          httpGet:
            path: /api/v1/health/liveness
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health/readiness
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
```

## Multi-Region Deployment

### Example: Different configurations per region
```
k8s/
├── overlays/
│   ├── us-west/
│   │   └── kustomization.yaml
│   ├── us-east/
│   │   └── kustomization.yaml
│   └── eu-central/
│       └── kustomization.yaml
```

Each with region-specific settings:
```yaml
# k8s/overlays/us-west/kustomization.yaml
resources:
  - ../../base

labels:
  - pairs:
      region: us-west

patches:
  - path: region-config-patch.yaml
```

## Applying Multiple Overlays

You can combine overlays using kustomize:
```bash
# Create a combined overlay
mkdir -p k8s/overlays/prod-us-west

cat > k8s/overlays/prod-us-west/kustomization.yaml <<EOF
resources:
  - ../prod
  - ../us-west
EOF

kubectl apply -k k8s/overlays/prod-us-west
```
