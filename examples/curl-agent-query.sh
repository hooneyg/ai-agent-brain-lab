#!/bin/bash

# A simple script to query the Agent Core API

AGENT_URL="http://localhost:8000/ask"

QUERY=${1:-"What is the standard procedure for deploying a new microservice?"}

echo "Sending query to AI Agent Brain: $QUERY"

curl -X POST "$AGENT_URL" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"$QUERY\"}" \
     | jq .
