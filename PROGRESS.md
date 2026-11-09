# Project progress

## 2026-11-09

Denzel reported that no work had started and that he is completing the extra-credit project alone. Scope: two event sources, Open-Meteo enrichment, minimal frontend, and required cloud components only.

Prepared initial application, nonroot Dockerfile, secret exclusions, and six synthetic-data unit tests. First test discovery failed because the command ran from the parent directory; running from the application directory resolved the import issue. All six tests pass. Tests cover normalization, source/link preservation, date ordering, separation by venue/date, missing venues, cancelled Ticketmaster events, and PredictHQ timezone conversion.

Pending: project/account access; deadline; instructor expectations for solo work; API keys and trial coverage; live API and HTTP checks; container build; repository; GCP setup and budget alert; load balancer; diagram/report; video; eventual teardown. No teammate contributions are claimed.

Local HTTP smoke checks passed for /health, /, /app.js, and /style.css. External requests and container execution remain unverified.

## Verified continuation — November 9, 2026

GCP console verified a Free Trial account with $300 remaining and 90 days, expiring February 8, 2027. Created a billing-account-wide $10 monthly alert budget excluding credits; actual usage alerts at $1, $5, and $10, with billing-admin/user emails enabled. This is not a hard cap or authorization for out-of-pocket spending. Authorized out-of-pocket maximum remains $0; no paid upgrade authorized. Current project: formidable-pact-514217-f2.

Reran all six synthetic tests successfully. HTTP smoke checks returned 200 for /health (body OK), /, /app.js, /style.css, and 400 for a one-character city. Docker is unavailable in the current workspace; container build remains unverified. GitHub CLI is installed but unauthenticated.

Ticketmaster developer app is approved with Public APIs enabled. A browser-based live query returned 12 Richmond, VA events for November 9–15. An initial copy-to-clipboard attempt yielded an empty value and the test returned Invalid ApiKey; reading the visible Consumer Key and retrying succeeded. No keys are included in this record. This verifies upstream access, not the full application's live search.

PredictHQ trial verified: 14 days remaining, global access, 200 requests/minute, max 50 results/page, 90-day past/future visibility, required attribution, no commercial use or data storage. User created an Events-API-only token named INFO520 City Events Finder. Corrected starter request limit from 100 to 50, added an assertion to the existing provider-normalization test, and updated the coverage note. Live PredictHQ access remains unverified.

Cloud Shell awaits user authorization. No Cloud Run, Artifact Registry, Secret Manager, or load-balancer resources have been created by the assistant. November 20 morning teardown reminder was created; it is not automatic deletion. Solo work and AI assistance are documented; no partner contributions or role swaps are claimed.

### Live and container verification

User authorized Cloud Shell. PredictHQ upstream request returned HTTP 200, 249 matching events, and 50 records on the requested page. Initial full app search returned 63 records but five were outside the city-local date window because the query used UTC calendar dates. Corrected both providers’ query boundaries to city-local midnight converted to UTC, with explicit local-date filtering for PredictHQ. Added a daylight-saving transition test. Seven tests pass; corrected live search yielded Ticketmaster 16, PredictHQ 50, Open-Meteo 7 dates, 65 final events after one duplicate within the combined input was removed. No cross-provider exact duplicate was found in this sample; fuzzy cross-provider detection is not claimed. All final records fell within the requested dates and had weather.

Docker builds passed in Cloud Shell. Container /health returned OK and container HTTP search reported all providers successful with 65 events. GitHub public repository created: denzel322/info520-city-events-finder; no commits pushed yet. Enabled Run, Artifact Registry, Secret Manager, Compute APIs. Artifact Registry repository city-events created in us-central1. Further secret/service-account creation is in progress and requires checking completion before claiming success. Added exact required attribution “Events by PredictHQ” after checking provider documentation. AI assistance includes code fixes and verification, not human partner collaboration.

Artifact Registry repository city-events, Secret Manager secrets ticketmaster-api-key and predicthq-api-token (version 1 each), and service account city-events-runtime were all confirmed created. No runtime secret-access grants or public service permissions have been applied yet. Container image push is in progress.

### Deployed and verified

GitHub CLI authorization completed as denzel322. The repository contains actual solo work and AI disclosure. The initial commit email configuration was corrected immediately; no partner identity or backdated commit was created. Secret-specific runtime grants were applied after explicit user approval. Cloud Run revision city-events-finder-00001-qbx deployed successfully with min 0, max 2, concurrency 8, 1 CPU, 256 MiB, port 8080, 60-second request timeout, secret version 1 references, startup/liveness /health probes, public invocation, and internal-and-cloud-load-balancing ingress. The deployed image digest is sha256:a56384549488f53aeca614167a7bc268cfed8bd5595a7769d8f4ddf7112608ac.

Created the global EXTERNAL_MANAGED HTTP load balancer with serverless NEG city-events-neg, backend city-events-backend, URL map city-events-map, proxy city-events-http-proxy, reserved IP city-events-ip (8.233.231.191), and forwarding rule city-events-http on port 80. The NEG is in us-central1. No VM-style load-balancer health check was created. Initial resets/closed connections and a 502 resolved during propagation without a configuration change.

Public HTTP acceptance checks from Cloud Shell passed: /health 200 OK, / and assets 200, invalid city 400, Richmond search complete with 65 sorted/weather-enriched events, zero duplicate keys and zero out-of-window dates. Direct external run.app /health returned 404. Browser automation blocked the IP with ERR_BLOCKED_BY_CLIENT; no visual browser result is claimed. No scale-out load test was performed.

Prepared a one-page diagram, three-page report, and 4:45 Zoom outline with solo and AI disclosures. Reflection remains for Denzel to personalize. The two-teammate rubric remains an instructor-accommodation question. Teardown scripts are syntax checked; destructive deletion has not run. The November 20 reminder is not automatic deletion. No assignment or demo was submitted or recorded.
