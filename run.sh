#!/bin/bash

# Book Advisor Application Startup Script

echo "🚀 Starting Book Advisor Application..."
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import mcp" 2>/dev/null || {
    echo "Installing MCP and dependencies..."
    pip install -r requirements.txt
}

# Kill any existing MCP server processes
echo "🧹 Cleaning up any existing processes..."
pkill -f "mcp dev server.py" 2>/dev/null
pkill -f "python server.py" 2>/dev/null
pkill -f "python app.py" 2>/dev/null

# Start the Flask application (which will start the MCP server internally)
echo ""
echo "🌐 Starting web server..."
echo "======================================"
echo "📍 Access the application at: http://localhost:5000"
echo "📍 Press Ctrl+C to stop the server"
echo "======================================"
echo ""

# Run the Flask app
python3 app.py