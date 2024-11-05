#!/bin/bash

# Set variables
CLUSTER_NAME="your-ecs-cluster-name"
SERVICES=("frontend-service" "backend-service")

# Scale down services to zero
for SERVICE in "${SERVICES[@]}"; do
  echo "Scaling down $SERVICE..."
  aws ecs update-service --cluster "$CLUSTER_NAME" --service "$SERVICE" --desired-count 0
done

echo "All services have been scaled down to zero."
