#!/bin/bash

echo "🔧 Installing Machine Hours System Dependencies..."

# Navigate to frontend directory
cd frontend

# Install Recharts for the machine hours chart
echo "📊 Installing Recharts for machine hours charts..."
npm install recharts

echo "✅ Dependencies installed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Restart your frontend development server"
echo "2. Hard refresh your browser (Shift+Cmd+R on Mac, Shift+Ctrl+R on Windows)"
echo "3. Login as zisis to test the reminder system"
echo "4. Check the Machines page for enhanced machine cards"
echo "5. Open machine details to see the new 'Machine Hours' tab"
echo ""
echo "🧪 To test the reminder API directly, run:"
echo "   python test_reminder_api.py"