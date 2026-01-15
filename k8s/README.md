# Sunona Voice AI - Kubernetes Configuration

Production-grade Kubernetes manifests for deploying Sunona Voice AI.

## Quick Deploy

```bash
cd k8s
chmod +x deploy.sh
./deploy.sh apply
```

## Files

| File | Description |
|------|-------------|
| `namespace.yaml` | Sunona namespace |
| `configmap.yaml` | Environment configuration |
| `secrets.yaml` | API keys and passwords (⚠️ EDIT BEFORE DEPLOY!) |
| `rbac.yaml` | ServiceAccount, Role, PodDisruptionBudget |
| `deployment.yaml` | Main API with HPA autoscaling (2-10 replicas) |
| `redis.yaml` | Redis StatefulSet with persistent storage |
| `postgres.yaml` | PostgreSQL StatefulSet with persistent storage |
| `ingress.yaml` | NGINX Ingress with TLS + Network Policy |
| `monitoring.yaml` | Prometheus ServiceMonitor |

## Prerequisites

1. **Kubernetes Cluster** (1.25+)
2. **NGINX Ingress Controller**
3. **cert-manager** (for TLS)
4. **Prometheus Operator** (optional, for monitoring)

## Configuration

### 1. Edit Secrets
```bash
# Edit secrets.yaml with your actual API keys
vim secrets.yaml
```

### 2. Update Ingress Domain
```bash
# Change api.sunona.ai to your domain
vim ingress.yaml
```

### 3. Deploy
```bash
kubectl apply -f namespace.yaml
kubectl apply -f rbac.yaml
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml
kubectl apply -f redis.yaml
kubectl apply -f postgres.yaml
kubectl apply -f deployment.yaml
kubectl apply -f ingress.yaml
```

## Scaling

```bash
# Manual scaling
kubectl scale deployment sunona-api -n sunona --replicas=5

# HPA handles automatic scaling based on CPU/Memory
kubectl get hpa -n sunona
```

## Monitoring

```bash
# View pods
kubectl get pods -n sunona

# View logs
kubectl logs -f deployment/sunona-api -n sunona

# Check health
kubectl exec -it deployment/sunona-api -n sunona -- curl localhost:8000/health
```

## Production Checklist

- [ ] Update `secrets.yaml` with real API keys
- [ ] Change default PostgreSQL password
- [ ] Update Ingress hostname to your domain
- [ ] Configure cert-manager for TLS
- [ ] Set up persistent storage class
- [ ] Configure backup for PostgreSQL
- [ ] Set up alerting in Prometheus
