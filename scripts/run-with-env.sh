#!/usr/bin/env bash
# Script to run commands with properly sourced environment variables

# Source the .env file
if [ -f ".env" ]; then
    source .env
elif [ -f "../.env" ]; then
    source ../.env
elif [ -f "../../.env" ]; then
    source ../../.env
elif [ -f "../../../.env" ]; then
    source ../../../.env
else
    echo "Error: .env file not found"
    exit 1
fi

# Export all variables for child processes
set -a
source .env 2>/dev/null || source ../.env 2>/dev/null || source ../../.env 2>/dev/null || source ../../../.env 2>/dev/null
set +a

# Run the command passed as arguments
exec "$@"