#!/bin/bash

# Set variables
CLUSTER_NAME="belief-state-machine-cluster"
SERVICES=("belief-state-machine-frontend-service" "belief-state-machine-backend-service")
DESIRED_COUNT=1  # Adjust as needed

# Scale up services
for SERVICE in "${SERVICES[@]}"; do
  echo "Scaling up $SERVICE to $DESIRED_COUNT..."
  aws ecs update-service --cluster "$CLUSTER_NAME" --service "$SERVICE" --region us-east-1 --desired-count "$DESIRED_COUNT"
done

echo "All services have been scaled up to $DESIRED_COUNT."
