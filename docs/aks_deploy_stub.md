# AKS Deploy (Stub)

## Build & push image (example with ACR)
# az acr build -r <ACR_NAME> -t <repo>:<tag> .

## Simple K8s manifest (example)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentops-demo
spec:
  replicas: 1
  selector:
    matchLabels: { app: agentops-demo }
  template:
    metadata:
      labels: { app: agentops-demo }
    spec:
      containers:
      - name: api
        image: <ACR_LOGIN>/agentops-demo:<tag>
        ports: [{ containerPort: 8000 }]
---
apiVersion: v1
kind: Service
metadata:
  name: agentops-svc
spec:
  type: ClusterIP
  selector: { app: agentops-demo }
  ports:
    - port: 80
      targetPort: 8000

## Expose via Ingress/Application Gateway as needed
# kubectl apply -f k8s.yaml
# kubectl rollout status deploy/agentops-demo
