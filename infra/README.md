# Infrastructure

## Google Cloud Platform

### Keda

Keda is a Kubernetes-based event-driven autoscaling component. It provides event-driven scale for any container in Kubernetes.

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace -f ./keda/values.yml
```

### Traefik

Traefik is a modern HTTP reverse proxy and load balancer that makes deploying microservices easy.

Dashboard Port Forward (<http://localhost:9000/dashboard/#/>):

```bash
k port-forward traefik-8474986d76-qpvl8 -n traefik 9000:9000
```

Instalcja

```bash
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
helm install --namespace traefik traefik traefik/traefik --create-namespace -f ./traefik/values.yml
kubectl apply -f ./traefik/default-ssl.yml
```

#### Monitoing - Kube Prometheus Stack

The kube-prometheus-stack provides a collection of Kubernetes manifests, Grafana dashboards, and Prometheus rules combined with documentation and scripts to provide easy to operate end-to-end Kubernetes cluster monitoring with Prometheus using the Prometheus Operator.

Docs: <https://prometheus-operator.dev>

GitHub: <https://github.com/prometheus-operator/kube-prometheus>

Grafana Port Forward:

```bash
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 3000:80
```

Prometheus Port Forward:

```bash
kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090
```

Alertmanager Port Forward:

```bash
kubectl port-forward svc/kube-prometheus-stack-alertmanager -n monitoring 9093
```

Instalcja

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace -f ./kube-prometheus/values.yml
```

### Cert Manager

Cert Manager is a Kubernetes addon to automate the management and issuance of TLS certificates from various issuing sources.

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.11.0 \
    --set installCRDs=true
```

Konfiguracja - <https://cert-manager.io/docs/configuration/acme/dns01/google/>

Service Account:

```bash
PROJECT_ID=<project-id-google>
gcloud iam service-accounts create dns01-solver --display-name "dns01-solver"
gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member serviceAccount:dns01-solver@$PROJECT_ID.iam.gserviceaccount.com \
   --role roles/dns.admin
gcloud iam service-accounts add-iam-policy-binding \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[cert-manager/cert-manager]" \
    dns01-solver@$PROJECT_ID.iam.gserviceaccount.com
kubectl annotate serviceaccount --namespace=cert-manager cert-manager \
    "iam.gke.io/gcp-service-account=dns01-solver@$PROJECT_ID.iam.gserviceaccount.com"
```

Certyfikaty:

```bash
kubectl apply -f ./cert-manager
```

### External DNS

ExternalDNS synchronizes exposed Kubernetes Services and Ingresses with DNS providers.

Instructions - <https://kubernetes-sigs.github.io/external-dns/v0.13.4/tutorials/gke/#configure-project-environment>

Create GSA for use with Workload Identity¶

```bash
PROJECT_ID=<project-id-google>
DNS_SA_NAME="external-dns"
DNS_SA_EMAIL="$DNS_SA_NAME@${PROJECT_ID}.iam.gserviceaccount.com"
EXTERNALDNS_NS=external-dns

gcloud iam service-accounts create $DNS_SA_NAME --display-name $DNS_SA_NAME
gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member serviceAccount:$DNS_SA_EMAIL --role "roles/dns.admin"
gcloud iam service-accounts add-iam-policy-binding $DNS_SA_EMAIL \
  --role "roles/iam.workloadIdentityUser" \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[${EXTERNALDNS_NS:-"default"}/external-dns]"

# deploy external-dns
kubectl apply -f external-dns

# Link KSA to GSA in Kubernetes
kubectl annotate serviceaccount "external-dns" \
  --namespace ${EXTERNALDNS_NS:-"default"} \
  "iam.gke.io/gcp-service-account=$DNS_SA_EMAIL"
```

### Network policies

Network policies are implemented by the network plugin, so you must be using a networking solution which supports NetworkPolicy - Calico.

```bash
kubectl apply -f ./policies
kubectl apply -f ./policies/monitoring
```
