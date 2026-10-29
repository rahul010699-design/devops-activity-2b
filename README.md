# DevOps Activity 2B — GKE Deployment, CI/CD and Monitoring

A Flask REST API deployed to Google Kubernetes Engine (GKE), integrated with Cloud SQL PostgreSQL and Secret Manager, with keyless GitHub Actions CI/CD, Kubernetes autoscaling, and Cloud Monitoring.

## Objectives

- Deploy a containerized Flask API to GKE.
- Configure Kubernetes Deployment, ClusterIP Service, and startup, readiness, and liveness probes.
- Define CPU and memory requests and limits.
- Configure Horizontal Pod Autoscaling (HPA).
- Connect to Cloud SQL PostgreSQL using Workload Identity and Secret Manager.
- Automate builds and deployments through GitHub Actions.
- Configure Cloud Monitoring dashboards and alert policies.
- Test recovery and document incidents.

## Architecture

```text
Developer
  |
  v
GitHub Repository (main)
  |
  v
GitHub Actions
  |-- Workload Identity Federation
  |-- Build and push Docker image
  |-- Deploy image to GKE
  v
GKE Development Cluster
  |-- Namespace: activity-2b
  |-- Flask API Deployment
  |-- ClusterIP Service
  |-- Health probes and HPA
  |
  |-- Workload Identity --> Secret Manager
  |-- Private connection --> Cloud SQL PostgreSQL
  |
  v
Cloud Monitoring dashboard and alert policies
```

## Technology Stack

- Python and Flask
- Docker
- Google Kubernetes Engine (GKE) and Kubernetes
- Cloud SQL for PostgreSQL
- Secret Manager and Workload Identity
- Artifact Registry
- GitHub Actions
- Cloud Monitoring

## Project Structure

```text
devops-activity-2b/
├── .github/workflows/deploy-gke.yml
├── app/
│   ├── app.py
│   ├── init_db.py
│   └── check_db_auth.py
├── docs/
│   └── incident-report.md
├── k8s/
│   ├── db-init-job.yaml
│   ├── db-auth-check.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── github-deployer-rbac.yaml
│   └── github-deployer-rolebinding.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application status message |
| GET | `/health` | Health check |
| GET | `/users` | Retrieve user records |
| POST | `/users` | Create a user record |

User records are stored in PostgreSQL.

## Kubernetes Configuration

- Namespace: `activity-2b`
- Deployment: `activity-2b-api`
- Service: `activity-2b-api`
- Service type: `ClusterIP`
- Container port: `5000`
- HPA minimum replicas: `1`
- HPA maximum replicas: `3`
- CPU utilization target: `70%`
- CPU request/limit: `100m` / `500m`
- Memory request/limit: `256Mi` / `512Mi`

Startup, readiness, and liveness probes use `/health`.

## Security

- GitHub Actions uses Workload Identity Federation instead of a service-account key file.
- The application uses a dedicated Kubernetes service account.
- Database credentials are retrieved from Secret Manager.
- Cloud SQL is accessed using its private IP address.
- IAM permissions are scoped to the required resources.
- Database passwords and service-account private keys are not stored in the repository.

## CI/CD

The workflow is `.github/workflows/deploy-gke.yml`. It runs on relevant pushes to `main` and supports manual execution.

The workflow checks out the repository, authenticates to Google Cloud, builds and pushes a Docker image tagged with the Git commit SHA, retrieves GKE credentials, updates the Deployment image, and waits for rollout completion.

**Validation:** The GitHub Actions build-and-deploy workflow completed successfully.

## Monitoring and Alerting

The Cloud Monitoring dashboard, `Activity 2B - GKE Monitoring`, includes:

- CPU request utilization
- Memory utilization
- HTTP request count

Alert policies were configured for HTTP 5xx errors, container or pod restarts, and HTTP request rate.

An external uptime check was deferred because the application is intentionally internal-only. Kubernetes health probes and manual API checks were used to validate application health.

## Failure Testing and Recovery

- **Pod deletion:** Kubernetes recreated the pod, and the previously saved database record remained available.
- **Scale-to-zero test:** The application temporarily had no pods. After restoring one replica, the Deployment recovered and the HPA returned to `ScalingActive=True` with a valid CPU metric.
- **Health check:** `/health` returned `healthy`.
- **Database check:** `/users` returned the saved `Activity 2B Test` record after recovery.

Temporary scheduling delays involving insufficient memory and a node taint were observed during pod recovery. See `docs/incident-report.md`.

## Deployment Access

The application is intentionally **internal-only** and uses a Kubernetes `ClusterIP` Service. No public application load balancer or Ingress was created.

For local testing, run:

```powershell
kubectl port-forward service/activity-2b-api 8080:80 -n activity-2b
```

Then use another PowerShell window:

```powershell
Invoke-RestMethod http://localhost:8080/health
Invoke-RestMethod http://localhost:8080/users
```

## Repository

https://github.com/rahul010699-design/devops-activity-2b

## Incident Report

See [`docs/incident-report.md`](docs/incident-report.md) for failure scenarios, recovery steps, validation results, and follow-up actions.
