#!/usr/bin/env bash
set -euo pipefail
PROJECT=formidable-pact-514217-f2
REGION=us-central1
gcloud compute forwarding-rules list --project="$PROJECT" --filter='name=city-events-http'
gcloud compute target-http-proxies list --project="$PROJECT" --filter='name=city-events-http-proxy'
gcloud compute url-maps list --project="$PROJECT" --filter='name=city-events-map'
gcloud compute backend-services list --project="$PROJECT" --filter='name=city-events-backend'
gcloud compute network-endpoint-groups list --project="$PROJECT" --filter='name=city-events-neg'
gcloud compute addresses list --project="$PROJECT" --filter='name=city-events-ip'
gcloud run services list --region="$REGION" --project="$PROJECT" --filter='metadata.name=city-events-finder'
gcloud artifacts repositories list --location="$REGION" --project="$PROJECT" --filter='name:city-events'
gcloud secrets list --project="$PROJECT" --filter='name:(ticketmaster-api-key OR predicthq-api-token)'
gcloud iam service-accounts list --project="$PROJECT" --filter='email:city-events-runtime@'
echo 'All named resources above should be absent. Also inspect the whole project inventory and delayed billing reports for unexpected resources.'
