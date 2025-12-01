#!/bin/bash

echo "Checking ABParts Services..."
echo "=============================="

echo -n "API (port 8000): "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo -n "Frontend (port 3000): "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo -n "Database (port 5432): "
if nc -z localhost 5432 2>/dev/null; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo -n "Redis (port 6379): "
if nc -z localhost 6379 2>/dev/null; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo ""
echo "Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep abparts
