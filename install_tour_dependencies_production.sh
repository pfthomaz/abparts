#!/bin/bash

echo "Installing tour system dependencies in production..."

# Navigate to frontend directory
cd frontend

# Install react-joyride for the guided tour functionality
npm install react-joyride

# Install heroicons for the help button icon
npm install @heroicons/react

echo "✅ Dependencies installed successfully!"
echo ""
echo "Next steps:"
echo "1. Run the translation script to add tour translations"
echo "2. Rebuild the frontend container"
echo "3. Restart the services"