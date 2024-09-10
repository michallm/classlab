<br />
<div align="center">
  <a href="https://github.com/michallm/classlab">
    <img src="classlab/static/images/favicons/favicon.ico" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">ClassLab</h3>

  <p align="center">
    Deploy and manage applications
    <!-- <br />
    <br />
    <a href="https://github.com/michallm/classlab">View Demo</a>
    ·
    <a href="https://github.com/michallm/classlab/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/michallm/classlab/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p> -->
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <!-- <li><a href="#license">License</a></li> -->
    <!-- <li><a href="#contact">Contact</a></li> -->
  </ol>
</details>

<!-- DEMO -->

## Demo

Click to watch the demo:

[![ClassLab demo](https://github.com/michallm/classlab/blob/main/images/preview.png?raw=true)](https://www.youtube.com/watch?v=UlLlNjXtSz4)

<!-- ABOUT THE PROJECT -->

## About The Project

ClassLab is a platform for deploying and managing applications. It is designed for education facilities and companies that want to provide their students or employees with a simple way to deploy and manage applications like Wordpress, Jupyter Notebook, or any other application that can be run in a container.

### Built With

- [![Django][Django.com]][Django-url]
- [![Docker][Docker.com]][Docker-url]
- [![Kubernetes][Kubernetes.com]][Kubernetes-url]

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps(it's not a easy task):

### Prerequisites

Only tested on MacOS.

- Python
- Docker
- Docker Compose
- Helm and Helmfile

  ```sh
  brew install helm
  brew install helmfile
  helmfile init
  ```

### Installation

1. Clone the repo

   ```sh
   git clone https://github.com/michallm/classlab.git
   ```

2. Build the docker images

   ```
   docker compose build
   ```

3. Apply migrations

   ```
   docker compose run --rm django python manage.py migrate
   ```

4. Load seed data

   ```
   docker compose run --rm django python manage.py loaddata fixtures/seed.json
   ```

5. Start the application

   ```
   docker compose up
   ```

<!-- USAGE -->

## Usage

### Accounts

#### Superuser

email: admin@example.com
password: zaq1@WSX

#### Organisation Admin

email: admin@test.com
password: zaq1@WSX

#### Sample Teacher

email: teacher@test.com
password: zaq1@WSX

#### Sample Student

email: student@test.com
password: zaq1@WSX

### Services

- Mailpit: http://localhost:8025
- Flower: http://localhost:5555
- Django admin: http://localhost:8000/admin
- Website: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:8080
  ```sh
  kubectl port-forward svc/kube-prometheus-stack-grafana 8080:80 -n monitoring
  ```

### Generate templates

```sh
cd templates
python generate.py -d -n <namespace>
```

<!-- ROADMAP -->

## Roadmap

- [ ] TCP Proxy
- [ ] Deployment of an application itself on Kubernetes
- [ ] More automated development process
- [ ] HTTPS for applications (development)

See the [open issues](https://github.com/michallm/classlab/issues) for a full list of proposed features (and known issues).

## Contact

<!-- Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com -->

Project Link: [https://github.com/michallm/classlab](https://github.com/michallm/classlab)

<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->

[contributors-shield]: https://img.shields.io/github/contributors/michallm/classlab.svg?style=for-the-badge
[contributors-url]: https://github.com/michallm/classlab/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/michallm/classlab.svg?style=for-the-badge
[forks-url]: https://github.com/michallm/classlab/network/members
[stars-shield]: https://img.shields.io/github/stars/michallm/classlab.svg?style=for-the-badge
[stars-url]: https://github.com/michallm/classlab/stargazers
[issues-shield]: https://img.shields.io/github/issues/michallm/classlab.svg?style=for-the-badge
[issues-url]: https://github.com/michallm/classlab/issues
[license-shield]: https://img.shields.io/github/license/michallm/classlab.svg?style=for-the-badge
[license-url]: https://github.com/michallm/classlab/blob/master/LICENSE.txt
[product-screenshot]: images/preview.png
[Django.com]: https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white
[Django-url]: https://www.djangoproject.com/
[Docker.com]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[Kubernetes.com]: https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white
[Kubernetes-url]: https://kubernetes.io/
