# Verification on November 9, 2026

Performed with Denzel's authorized accounts and ChatGPT assistance. These are observed results, not claims of partner work.

## Application and container

- Seven synthetic unit tests passed in the workspace and Google Cloud Shell.
- Docker build passed; image ran as the configured nonroot user.
- Container `/health`: HTTP 200, body `OK`.
- Container `/api/events?city=Richmond`: all three providers succeeded; 65 events.
- Image pushed to Artifact Registry with digest `sha256:a56384549488f53aeca614167a7bc268cfed8bd5595a7769d8f4ddf7112608ac`.

## Public load-balancer route

Tests used Python HTTP requests from Cloud Shell to http://8.233.231.191.

| Check | Observed result |
|---|---|
| `/health` | 200, body `OK` |
| Richmond search | Location Richmond, Virginia, United States |
| Providers | Ticketmaster 16; PredictHQ 50; Open-Meteo 7 forecast dates; all successful |
| Final result count | 65 |
| Chronological sort | Passed (date, local time, title) |
| Duplicate normalized keys | 0 |
| Dates outside local seven-day window | 0 |
| Events with weather | 65 |
| `/`, `/app.js`, `/style.css` | 200 each |
| `/api/events?city=x` | 400 |
| Direct external Cloud Run `/health` | 404 with restricted ingress |

The load balancer first reset/closed connections, then returned one 502 during propagation. A later readiness check returned 200 and all acceptance checks passed. No infrastructure mutation was needed between the transient errors and success.

The combined provider input held 66 records and 65 final keys; one repeated key was removed. No cross-provider exact match was observed in this sample. Synthetic tests verify retaining both sources/links for an exact match. Different titles for the same real event may remain separate, and same-title/date/venue performances may be collapsed by the simple rule.

Browser automation reported `ERR_BLOCKED_BY_CLIENT` when opening the public IP. It did not render or visually inspect the deployed UI. Manual browser verification remains a pre-demo task. No load test or measured scale-out is claimed. Teardown is pending November 20.

## Cloud configuration

Cloud Run revision `city-events-finder-00001-qbx` reported Ready and 100% traffic. Verified container port 8080, concurrency 8, 1 CPU, 256 MiB, 60s timeout, service maximum 2, and default/explicitly requested minimum 0. Startup and liveness probe settings, runtime service account, secret version references, and `internal-and-cloud-load-balancing` ingress were inspected. The global EXTERNAL_MANAGED HTTP frontend maps to a serverless NEG in us-central1. No VM-style load-balancer health check was created.

API keys were excluded from committed files and the image. Exact credential-value checks against Git history returned false for both API credentials. Docker image configuration also contained neither credential value. The Dockerfile copies only runtime source files, and no credentials were supplied as build arguments or baked environment values. No credential values are included in these notes. Billing alerts and the unupgraded Free Trial account were verified. No out-of-pocket spending is authorized.
