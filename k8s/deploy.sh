#!/bin/bash
# Sunona Voice AI - Kubernetes Deployment Script
# Usage: ./deploy.sh [apply|delete]

set -e

NAMESPACE="sunona"
ACTION="${1:-apply}"

echo "========================================="
echo "  SUNONA VOICE AI - K8S DEPLOYMENT"
echo "  Action: $ACTION"
echo "========================================="

# Apply in order (dependencies first)
if [ "$ACTION" = "apply" ]; then
    echo "Creating namespace..."
    kubectl apply -f namespace.yaml
    
    echo "Creating RBAC..."
    kubectl apply -f rbac.yaml
    
    echo "Creating secrets and config..."
    kubectl apply -f secrets.yaml
    kubectl apply -f configmap.yaml
    
    echo "Deploying Redis..."
    kubectl apply -f redis.yaml
    
    echo "Deploying PostgreSQL..."
    kubectl apply -f postgres.yaml
    
    echo "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=120s
    kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=120s
    
    echo "Deploying Sunona API..."
    kubectl apply -f deployment.yaml
    
    echo "Creating Ingress..."
    kubectl apply -f ingress.yaml
    
    echo "Setting up monitoring..."
    kubectl apply -f monitoring.yaml 2>/dev/null || echo "Monitoring CRDs not installed, skipping..."
    
    echo ""
    echo "========================================="
    echo "  DEPLOYMENT COMPLETE!"
    echo "========================================="
    echo ""
    kubectl get pods -n $NAMESPACE
    echo ""
    echo "Check status: kubectl get all -n $NAMESPACE"
    echo "View logs:    kubectl logs -f deployment/sunona-api -n $NAMESPACE"
    
elif [ "$ACTION" = "delete" ]; then
    echo "Deleting all resources..."
    kubectl delete -f . --ignore-not-found
    echo "Done!"
else
    echo "Usage: ./deploy.sh [apply|delete]"
    exit 1
fi
