# Ignatius Chat Web App

A simple web interface for interacting with the Ignatius debate chatbot API.

## Features

- Clean, responsive chat interface
- Real-time conversation with the Ignatius AI bot
- Conversation persistence and management
- Connection status monitoring
- Mobile-friendly design

## Quick Start

1. **Start the Ignatius API service:**
   ```bash
   # From the main project directory
   make run
   ```

2. **Start the web app server:**
   ```bash
   # From the webapp directory
   python server.py
   ```

3. **Open your browser:**
   The app will automatically open at `http://localhost:8080`

## Manual Setup

If you prefer to serve the files differently:

1. Serve the HTML files using any web server
2. Ensure the API is running on `http://localhost:5001`
3. Open `index.html` in your browser

## Files

- `index.html` - Main chat interface
- `style.css` - Styling and responsive design
- `script.js` - JavaScript for API communication and chat functionality
- `server.py` - Simple Python HTTP server with CORS support
- `README.md` - This file

## API Configuration

The web app connects to the Ignatius API at `http://localhost:5001/api/v1` by default. 

To change the API URL, edit the `apiBaseUrl` property in `script.js`:

```javascript
this.apiBaseUrl = 'http://your-api-url:port/api/v1';
```
