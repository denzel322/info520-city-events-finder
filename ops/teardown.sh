#!/usr/bin/env bash
# Run on November 20, 2026 after preserving evidence and checking grading needs.
set -euo pipefail
PROJECT=formidable-pact-514217-f2
REGION=us-central1
if [[ ${1:-} != --execute ]]; then
  echo "Deletes only the named INFO520 resources in $PROJECT."
  echo "Review this file, then run bash ops/teardown.sh --execute on the agreed teardown date."
  exit 0
fi
gcloud compute forwarding-rules delete city-events-http --global --project="$PROJECT" --quiet
gcloud compute target-http-proxies delete city-events-http-proxy --global --project="$PROJECT" --quiet
gcloud compute url-maps delete city-events-map --global --project="$PROJECT" --quiet
gcloud compute backend-services delete city-events-backend --global --project="$PROJECT" --quiet
gcloud compute network-endpoint-groups delete city-events-neg --region="$REGION" --project="$PROJECT" --quiet
gcloud compute addresses delete city-events-ip --global --project="$PROJECT" --quiet
gcloud run services delete city-events-finder --region="$REGION" --project="$PROJECT" --quiet
gcloud artifacts repositories delete city-events --location="$REGION" --project="$PROJECT" --quiet
gcloud secrets delete ticketmaster-api-key --project="$PROJECT" --quiet
gcloud secrets delete predicthq-api-token --project="$PROJECT" --quiet
gcloud iam service-accounts delete "city-events-runtime@$PROJECT.iam.gserviceaccount.com" --project="$PROJECT" --quiet
bash ops/verify-removal.sh
