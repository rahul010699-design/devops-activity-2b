# DevOps Activity 2B — Incident Report

## 1. Environment

- Platform: Google Kubernetes Engine (GKE)
- Cluster: activity-2a-dev-gke
- Namespace: activity-2b
- Application: activity-2b-api
- Database: Cloud SQL PostgreSQL — activity2b

## 2. Incident A — Pod Deletion and Recovery

### Scenario
A running application pod was deliberately deleted to test Kubernetes self-healing.

### Observations
- Kubernetes created a replacement pod through the Deployment's ReplicaSet.
- The replacement experienced temporary scheduling delays.
- Events reported insufficient memory and a node taint.
- A startup probe briefly failed while the application was starting.

### Recovery and verification
- The replacement pod reached Running and Ready.
- The Deployment rollout completed successfully.
- The health endpoint returned `healthy`.
- The `/users` endpoint returned the previously saved `Activity 2B Test` record.

### Outcome
Recovery succeeded. The application recovered and the database record persisted after pod recreation.

## 3. Incident B — Controlled Scale-to-Zero Test

### Scenario
The Deployment was deliberately scaled to zero replicas to simulate an application outage.

### Observations
- No application pods were available while the Deployment was scaled to zero.
- The HPA reported `ScalingActive=False` and `ScalingDisabled` because the target Deployment had zero replicas.

### Recovery and verification
- The Deployment was scaled back to one replica.
- The rollout completed successfully.
- The pod returned to Running and Ready.
- The HPA returned to `ScalingActive=True` with reason `ValidMetricFound`.
- Current CPU utilization was reported as 1% against a 70% target.
- The configured replica range is 1–3.

### Outcome
Recovery succeeded. The HPA resumed calculating replica recommendations after the Deployment was restored to one replica.

## 4. Final Validation

| Check | Result |
|---|---|
| Deployment availability | 1/1 |
| Pod readiness | 1/1 Running |
| Health endpoint | Passed |
| Database read | Passed |
| Data persistence after pod recreation | Passed |
| HPA metrics | Available |
| HPA scaling condition | Active |
| GitHub Actions build and deployment | Passed |
| Public load balancer | Not created; internal-only access retained |

## 5. Follow-up Actions

1. Review node capacity and scheduling events if memory-related delays recur.
2. Continue monitoring HPA metric availability and pod readiness.
3. Review Cloud Monitoring dashboards and alert policies.
4. Capture screenshots of the successful CI/CD run, monitoring dashboard, alert policies, and recovery checks.
5. An external uptime check was deferred because the application is intentionally internal-only.

## 6. Conclusion

The controlled failure tests demonstrated Kubernetes pod recovery, application health, database persistence, and restoration of HPA operation after scaling the Deployment back to one replica. The application remains configured for internal-only access.
