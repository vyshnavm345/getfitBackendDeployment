# GETFITBACKENDDEPLOYMENT

> **Deploy Effortlessly, Scale Seamlessly, Succeed Together**

![Last Commit](https://img.shields.io/github/last-commit/vyshnavm345/getfitBackendDeployment)  
![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Docker](https://img.shields.io/badge/docker-✅-blue) ![Django](https://img.shields.io/badge/django-REST-green)

Built with the tools and technologies:  
`Docker` • `Django` • `Nginx` • `PostgreSQL` • `Redis` • `Gunicorn` • `AWS EC2` • `YAML`

---

## 📚 Table of Contents

- [Overview](#overview)
- [What is GetFitBackendDeployment?](#why-getfitbackenddeployment)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)

---

## 🧭 Overview

**GetFitBackendDeployment** is a powerful solution to streamline the deployment of a containerized Django backend using Docker and Nginx, hosted on AWS EC2.

It is structured for scalability, modularity, and ease of use — making backend deployment faster and cleaner for development and production environments.

---

## 🚀 What is GetFitBackendDeployment?

This is the backend API for the website GetFitToday.xyz. This project simplifies the deployment process while ensuring scalability and efficiency. Core features include:

- 🚢 **Containerized Deployment**: Easily launch Django with Nginx using Docker.
- 🔄 **Multi-Service Architecture**: Integrated support for PostgreSQL, Redis, and Gunicorn via Docker Compose.
- 🛡️ **User Management**: Secure and scalable authentication/authorization logic.
- 💾 **Database Restore Scripts**: Reliable data backup and restoration support.
- 💬 **WebSocket Support**: Real-time communication enabled.
- ✅ **Robust Testing Framework**: Ensures production-readiness with unit/integration tests.

---

## 🏁 Getting Started

### ✅ Prerequisites

Ensure the following are installed:

- **Programming Language:** Python 3.10+
- **Package Manager:** Pip
- **Container Runtime:** Docker & Docker Compose
- **Cloud Deployment Option:** AWS EC2

---

### 🧰 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/vyshnavm345/getfitBackendDeployment.git
cd getfitBackendDeployment
```

2. **Set up environment variables:**

Copy the example `.env` file and customize it:

```bash
cp .env.example .env
```

Edit `.env` with your preferred credentials:

```env
# Example .env content
DEBUG=True
SECRET_KEY=your_django_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=getfit_db
POSTGRES_USER=getfit_user
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
```

> ⚠️ **Note:** Never commit your actual `.env` file with secrets to version control.

3. **Build and run the Docker containers:**

```bash
docker-compose up --build
```

This will launch the following services:

- 🚀 Django backend (via Gunicorn)
- 🐘 PostgreSQL
- 🔁 Redis
- 🌐 Nginx reverse proxy

4. **Apply migrations and create a superuser:**

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

5. **Collect static files:**

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

---

### ▶️ Usage

After setup, access the services at:

- 🧠 **API Root**: [
https://www.server.getfittoday.xyz/api/](
https://www.server.getfittoday.xyz/api/)
- 🔐 **Admin Panel**: [
https://www.server.getfittoday.xyz/admin](
https://www.server.getfittoday.xyz/admin/)

> 🛠️ In production, replace `localhost` with your domain or public IP (e.g., EC2 IP).

---
