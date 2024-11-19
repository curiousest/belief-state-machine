#!/bin/bash

# Set variables
CLUSTER_NAME="belief-state-machine-cluster"
SERVICES=("belief-state-machine-frontend-service" "belief-state-machine-backend-service")

# Scale down services to zero
for SERVICE in "${SERVICES[@]}"; do
  echo "Scaling down $SERVICE..."
  aws ecs update-service --cluster "$CLUSTER_NAME" --service "$SERVICE" --region us-east-1 --desired-count 0
done

echo "All services have been scaled down to zero."
