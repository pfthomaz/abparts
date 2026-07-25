#!/bin/bash
# install_tour_dependencies.sh
# Install required dependencies for the tour system

echo "Installing tour system dependencies..."

cd frontend

# Install react-joyride for guided tours
echo "Installing react-joyride..."
npm install react-joyride

# Install heroicons for icons
echo "Installing heroicons..."
npm install @heroicons/react

echo "✅ Tour dependencies installed successfully!"
echo ""
echo "Dependencies installed:"
echo "- react-joyride: Interactive guided tours"
echo "- @heroicons/react: Icon library for UI elements"
echo ""
echo "You can now start your development server:"
echo "npm start"