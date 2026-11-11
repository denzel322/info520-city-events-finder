# City Events Finder

INFO 520 extra-credit project by Denzel Speed, with ChatGPT assistance. Development and deployment are currently individual work. No partner contributions or role swaps are claimed.

- Application: http://8.233.231.191
- Health endpoint: http://8.233.231.191/health
- Repository: https://github.com/denzel322/info520-city-events-finder
- Deadline and planned teardown: November 20, 2026

## Verified on November 9, 2026

Seven synthetic-data tests passed. Both event APIs and Open-Meteo worked in the application. Docker build, container execution, and the deployed load-balancer route passed HTTP checks. The public Richmond search returned 65 sorted events, all inside the requested dates and all weather enriched. No duplicate keys remained. The frontend HTML and assets returned 200; invalid city input returned 400; `/health` returned 200 with `OK`. The direct external Cloud Run URL returned 404, consistent with the ingress restriction.

Browser automation was blocked from opening the public IP, so visual browser verification remains a manual check before recording. A load-induced scale-out test was not performed. Cleanup is prepared, not completed or automatically scheduled for deletion. See [VERIFICATION.md](VERIFICATION.md) and [PROGRESS.md](PROGRESS.md) for actual evidence and troubleshooting.

## Run locally

Python 3.12 or later is sufficient; the application has no third-party Python dependencies.

1. Obtain Ticketmaster Discovery API and PredictHQ Events API credentials. Confirm free access, geography, dates, and provider terms.
2. Set `TICKETMASTER_API_KEY` and `PREDICTHQ_API_TOKEN` in the shell environment. The app does not load `.env` files automatically. Never commit credentials.
3. Run `python3 app.py` from the repository root.
4. Open http://localhost:8080 and search a city such as `Richmond`.
5. Open http://localhost:8080/health to see `OK`.

Run the tests from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The tests use synthetic fixtures and cover normalization, source/link preservation, venue/date separation, missing venues, sorting, cancelled Ticketmaster events, PredictHQ local time conversion and request limit, and a daylight-saving boundary. Live integration results are recorded separately.

## Sources and behavior

Ticketmaster and PredictHQ return actual events. Open-Meteo supplies geocoding and weather, without a key for this noncommercial project. Queries cover the next seven calendar days in roughly a 15-mile radius. The first geocoding match is used; the resolved city, administrative area, and country are shown to make ambiguity visible.

Results are limited to 200 Ticketmaster and 50 PredictHQ records per search. The API response and UI disclose this bounded coverage. Requests run concurrently with 12-second provider timeouts. Date-only records can include events earlier today. No event database or caching is used. Forecast values are Fahrenheit and refer to the searched city. Provider failures are reported as partial results; no fake data is substituted.

Duplicate rule: normalize title and venue by lowercasing, removing punctuation, and folding accents, then compare title + local date + venue. Matching records retain source labels and links. Missing venues stay separate by source/ID. Sort by local date, time, then title; unknown times go last. Query bounds use city-local midnights converted to UTC. PredictHQ dates are converted to the event's timezone and filtered to the requested dates. This simple rule can miss differently titled duplicates and merge multiple same-day performances. A live 66-record input produced 65 final records. No exact cross-provider match appeared in that sample; the synthetic test covers combining both providers' labels/links.

PredictHQ's trial showed 14 days remaining on November 9, global access, 200 requests/minute, 50 records/page, 90-day historic/future visibility, attribution required, commercial use disallowed, and data storage disallowed. The UI displays **Events by PredictHQ**. Do not add stored real event fixtures or response caching without checking entitlement.

## Container

```bash
docker build -t city-events-finder .
docker run --rm -p 8080:8080 --env TICKETMASTER_API_KEY --env PREDICTHQ_API_TOKEN city-events-finder
```

The image copies only the four runtime files and runs as UID 10001. API credentials are supplied at runtime; they are not baked into the image. Container build and HTTP tests passed in Google Cloud Shell.

## Deployed Google Cloud configuration

Project: `formidable-pact-514217-f2`. Region: `us-central1`. Image:

```text
us-central1-docker.pkg.dev/formidable-pact-514217-f2/city-events/city-events-finder@sha256:a56384549488f53aeca614167a7bc268cfed8bd5595a7769d8f4ddf7112608ac
```

Cloud Run service `city-events-finder` uses min 0, service max 2, concurrency 8, 1 vCPU, 256 MiB, a 60-second timeout, and container port 8080. Zero minimum allows idle scale-down; max 2 and modest concurrency suit the small classroom workload. Startup probe: `/health`, period 10s, timeout 1s, failure threshold 3. Liveness probe: `/health`, period 30s, timeout 1s, failure threshold 3. Both use HTTP on 8080.

Runtime identity `city-events-runtime@formidable-pact-514217-f2.iam.gserviceaccount.com` has Secret Accessor separately on `ticketmaster-api-key` and `predicthq-api-token`. Cloud Run binds version 1 of each. Non-sensitive configuration may use ordinary environment variables. No service-account key was created.

Ingress is `internal-and-cloud-load-balancing`, and public invocation is allowed so the external load balancer can serve the app. Direct external `run.app` requests are rejected. The global external Application Load Balancer uses `EXTERNAL_MANAGED`, Premium tier, HTTP port 80, reserved address `city-events-ip` (8.233.231.191), forwarding rule `city-events-http`, proxy `city-events-http-proxy`, URL map `city-events-map`, backend `city-events-backend`, and regional serverless NEG `city-events-neg` targeting Cloud Run. No domain, HTTPS certificate, Cloud Armor, or optional load test was added.

Serverless NEGs do not use VM-style load-balancer health checks. `/health` is used by Cloud Run probes and by manual/public HTTP acceptance tests. Cloud Run reported Ready, and the LB health request returned `200 OK`.

Deployment sequence: enable Run, Artifact Registry, Secret Manager, and Compute APIs; create the Docker repository; build/tag/push the image; create both secrets and the runtime identity; grant the two secret-specific roles; deploy the image with the settings above; create the serverless NEG, global backend, URL map, HTTP proxy, IP, and forwarding rule. Allow time for load-balancer propagation before diagnosing transient resets or 502 responses.

## Cost controls and cleanup

Maximum authorized out-of-pocket spending is **$0**. The account was verified as a Free Trial account with $300 and 90 days remaining on November 9, ending February 8, 2027. Do not upgrade to paid billing. A $10 monthly billing-account budget excludes credits and emails billing admins/users at $1, $5, and $10 of actual usage. This is an alert, not a hard cap or permission to spend out of pocket. Billing data is delayed.

A reminder is set for November 20 in the morning. Automatic deletion is not configured. On that date, preserve required evidence, review the exact resources, and run:

```bash
bash ops/teardown.sh                 # preview only
bash ops/teardown.sh --execute       # destructive cleanup of the named project resources
bash ops/verify-removal.sh           # every named resource should be absent
```

The teardown script removes the forwarding rule, proxy, URL map, backend, NEG, reserved IP, Cloud Run service, Artifact Registry repository/images, secrets, and runtime service account. If a partial cleanup fails, inspect the actual inventory before resuming. Check the entire project for unexpected resources and delayed billing entries. Removal has not yet been verified because the agreed date is November 20.

