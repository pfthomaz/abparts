#!/bin/bash
echo "🔄 Restarting API..."
docker-compose restart api
echo "✅ API restarted! Wait 5 seconds for it to be ready..."
sleep 5
echo "✅ Ready! Try updating the user again."
