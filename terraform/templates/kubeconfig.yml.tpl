apiVersion: v1
clusters:
  - cluster:
      certificate-authority-data: ${cluster_ca_certificate}
      server: https://${endpoint}
    name: ${cluster_name}
contexts:
  - context:
      cluster: ${cluster_name}
      namespace: default
      user: ${user_name}
    name: ${cluster_name}
current-context: ${cluster_name}
kind: Config
users:
  - name: ${user_name}
    user:
      token: ${token}
