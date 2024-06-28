# Makefile for managing the project

.PHONY: minikube

stop: minikube-stop

minikube:
	@echo "Starting Minikube..."
	@minikube start --network-plugin=cni --cni=calico --profile=classlab --driver=docker --embed-certs --apiserver-names host.docker.internal --addons=ingress-dns,ingress,metrics-server,gvisor --install-addons=true --container-runtime=containerd --docker-opt containerd=/var/run/containerd/containerd.sock
	@echo "Exporting kubeconfig..."
	@kubectl config view --raw > kubeconfig
	@echo "Replacing 127.0.0.1 with host.docker.internal in kubeconfig..."
	@sed -i '' -e 's/127.0.0.1/host.docker.internal/g' kubeconfig
	@echo "Starting Minikube tunnel..."
	@minikube tunnel --profile=classlab

minikube-stop:
	@echo "Stopping Minikube..."
	@minikube stop --profile=classlab
	@echo "Minikube stopped."

start:
	docker compose up

dashboard:
	@echo "Starting Kubernetes Dashboard..."
	@minikube dashboard --profile=classlab
