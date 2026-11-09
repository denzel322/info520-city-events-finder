# City Events Finder

A small INFO 520 application that combines upcoming events from Ticketmaster and PredictHQ and enriches them with Open-Meteo weather. Author: Denzel Speed. Work is being completed individually; do not claim partner commits or a role swap that did not occur.

## Current status

Seven synthetic-data tests pass, including a daylight-saving boundary test. Live application search from Google Cloud Shell connected to Ticketmaster, PredictHQ, and Open-Meteo and returned 65 sorted Richmond-area events for November 9–15, 2026. All 65 were inside the local date window and weather enriched. Docker build and container HTTP checks passed. Cloud deployment and load balancer remain pending. GitHub repository exists at https://github.com/denzel322/info520-city-events-finder but code push is pending authentication.

## Run locally

Python 3.12 or later is sufficient; no Python dependencies are required.

1. Register for a Ticketmaster developer key and a PredictHQ trial/token. Confirm the latter covers your demonstration city and dates. Do not activate a short trial too early; verify access lasts through grading. Review each provider's terms for the intended classroom demo.
2. Set `TICKETMASTER_API_KEY` and `PREDICTHQ_API_TOKEN` in your shell environment. The app does not automatically load `.env` files. Keep credentials out of source files, screenshots, and commits.
3. From this directory run `python app.py`.
4. Open http://localhost:8080 and search a city such as Richmond, Virginia. The app displays the resolved city so ambiguous locations are visible.
5. Open http://localhost:8080/health. It returns plain text `OK`.

Open-Meteo weather and geocoding require no key for this noncommercial project. Forecast values are in Fahrenheit and refer to the searched city. API responses and error messages indicate which sources are unavailable; no fabricated results are substituted.

## Behavior and limits

Searches cover the next seven calendar days, including today, in roughly a 15-mile radius. Geocoding uses the first match and displays the resolved administrative area/country. Event search is intentionally capped at 200 Ticketmaster and 50 PredictHQ records; results are not exhaustive and this limit is disclosed in the UI. Date-only event records may include events earlier today. Provider query timestamps use the searched city’s local calendar boundaries converted to UTC. PredictHQ results are additionally filtered by local date. Provider requests have 12-second timeouts and run concurrently. Each search fetches fresh data; no optional cache is included.

An event is considered a duplicate when its title and venue (lowercase, punctuation removed, accents normalized) and local date all match. Keep both source names and available links when merged. If a venue is missing, keep records separate to avoid false merges. Different performances at the same venue on the same date may be merged by this simple rule; compare real results before finalizing the report. Results sort by local date and time. Unknown times sort last within a date. PredictHQ timestamps are converted to the event's timezone before comparison.

## Verify

Run `python -m unittest discover -s tests -v` from this directory. Tests use synthetic fixtures; they do not establish that live credentials work. Additional acceptance checks: real results from both feeds, weather enrichment, successful city resolution, one deliberate duplicate comparison, and graceful handling of unavailable sources.

## Container

Build with `docker build -t city-events-finder .` and run with `docker run --rm -p 8080:8080 --env TICKETMASTER_API_KEY --env PREDICTHQ_API_TOKEN city-events-finder`. The image copies only the four runtime files and runs as a nonroot user. Docker build and container execution were verified in Cloud Shell on November 9, 2026.

## Required GCP deployment still to perform

Before creating billable resources, confirm project ID, billing/trial credits, spending allowance, and grading date. Set a budget alert first; an alert is not a hard spending cap.

Build and push the Docker image to Artifact Registry. Deploy it to Cloud Run with keys referenced from Secret Manager, using a dedicated service account granted access only to the required secrets. Proposed low-traffic starting settings: minimum instances 0, maximum instances 2, concurrency 8, container port 8080. These are proposed values, not deployed settings. Configure startup/liveness probes against `/health` as appropriate.

Create the required external HTTP(S) load balancer with a serverless NEG targeting Cloud Run. Validate traffic end to end through the load balancer. Serverless NEGs do not use VM-style load balancer health checks; explain Cloud Run probes and manual `/health` validation instead. Restrict ingress to internal and cloud load balancing if using that optional hardening; verify the load balancer can reach the service before restricting access.

Artifact Registry and secret preparation began on November 9, 2026; consult PROGRESS.md for verified resource status. No deployed Cloud Run or load balancer is verified yet. The one-page architecture diagram and 2–3 page final report must reflect actual deployed settings and observed troubleshooting. Record a Zoom demo under five minutes. Explain solo participation accurately and check the instructor's expectations for solo extra credit. Remove billable resources after grading, including the load balancer, forwarding rules, IP address, Cloud Run service, images, and secrets when no longer needed.

## References

- Assignment: info520 - GCP Group Project (1).docx supplied by the user.
- https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
- https://docs.predicthq.com/api/events/search-events
- https://www.predicthq.com/pricing
- https://open-meteo.com/en/docs/geocoding-api
- https://open-meteo.com/en/docs

## AI disclosure

OpenAI. (2026, November 9). City Events Finder implementation and setup assistance [Generative AI chat]. ChatGPT. AI assisted with initial application code, unit tests, and this README. These outputs require live API and deployment verification. The first test invocation failed because it ran outside the application directory; rerunning from the documented project directory passed all six tests. No human collaboration or live-cloud results have been invented.

## Financial and trial constraints

Out-of-pocket allowance: $0. GCP remains a Free Trial account with $300 verified remaining on November 9; do not upgrade to paid billing. A $10 monthly gross-usage alert budget emails billing admins/users at $1, $5, and $10; it is not a hard cap. Deadline and teardown date: November 20, 2026. A reminder exists, not automatic deletion. PredictHQ trial showed 14 days remaining on November 9, global access, maximum 50 records/page, required attribution, no commercial use or data storage. The app does not persist event payloads or cache responses.
