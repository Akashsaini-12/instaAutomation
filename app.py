"""
app.py

Optional Flask web interface for  automation.
Provides a simple web UI for entering URLs and monitoring progress.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from pathlib import Path
from main import Automation
import threading
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to track automation status
automation_status = {
    "running": False,
    "progress": {},
    "results": None
}


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/submit', methods=['POST'])
def submit_urls():
    """Submit URLs for automation."""
    global automation_status
    
    if automation_status["running"]:
        return jsonify({"error": "Automation is already running"}), 400
    
    data = request.json
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400
    
    # Start automation in background thread
    automation_status["running"] = True
    automation_status["progress"] = {"status": "starting"}
    
    thread = threading.Thread(target=run_automation_background, args=(urls,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Automation started", "urls_count": len(urls)})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current automation status."""
    return jsonify(automation_status)


def run_automation_background(urls):
    """Run automation in background thread."""
    global automation_status
    
    try:
        config_path = "config.json"
        if not os.path.exists(config_path):
            automation_status["results"] = {"error": "Config file not found"}
            automation_status["running"] = False
            return
        
        automation = Automation(config_path=config_path)
        
        automation_status["progress"] = {"status": "downloading"}
        results = automation.run_automation(urls)
        
        automation_status["results"] = results
        automation_status["progress"] = {"status": "completed"}
        
    except Exception as e:
        logger.error(f"Automation error: {e}")
        automation_status["results"] = {"error": str(e)}
        automation_status["progress"] = {"status": "error"}
    
    finally:
        automation_status["running"] = False


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get automation results."""
    results_file = Path("downloads/automation_results.json")
    
    if results_file.exists():
        with open(results_file, 'r') as f:
            results = json.load(f)
        return jsonify(results)
    
    return jsonify({"error": "No results found"}), 404


def create_html_template(template_file):
    """Create a simple HTML template for the web UI."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> Automation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            resize: vertical;
            font-family: inherit;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        .status.info {
            background: #e3f2fd;
            color: #1976d2;
        }
        .status.success {
            background: #e8f5e9;
            color: #388e3c;
        }
        .status.error {
            background: #ffebee;
            color: #c62828;
        }
        .results {
            margin-top: 20px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            display: none;
        }
        .help-text {
            color: #888;
            font-size: 12px;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📸  Video Automation</h1>
        
        <form id="urlForm">
            <div class="form-group">
                <label for="urls">Enter  Video URLs (one per line):</label>
                <textarea id="urls" rows="8" placeholder="https://www..com/p/SHORTCODE1/&#10;https://www..com/reel/SHORTCODE2/&#10;..."></textarea>
                <div class="help-text">Paste  post or reel URLs, one per line</div>
            </div>
            <button type="submit" id="submitBtn">Start Automation</button>
        </form>
        
        <div id="status" class="status"></div>
        <div id="results" class="results"></div>
    </div>
    
    <script>
        const form = document.getElementById('urlForm');
        const statusDiv = document.getElementById('status');
        const resultsDiv = document.getElementById('results');
        const submitBtn = document.getElementById('submitBtn');
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const urlsText = document.getElementById('urls').value;
            const urls = urlsText.split('\\n')
                .map(url => url.trim())
                .filter(url => url && url.startsWith('http'));
            
            if (urls.length === 0) {
                showStatus('Please enter at least one valid URL', 'error');
                return;
            }
            
            submitBtn.disabled = true;
            showStatus('Starting automation...', 'info');
            
            try {
                const response = await fetch('/api/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ urls })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showStatus(`Automation started! Processing ${data.urls_count} videos...`, 'info');
                    startPolling();
                } else {
                    showStatus(data.error || 'Failed to start automation', 'error');
                    submitBtn.disabled = false;
                }
            } catch (error) {
                showStatus('Error: ' + error.message, 'error');
                submitBtn.disabled = false;
            }
        });
        
        function showStatus(message, type) {
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
        }
        
        function startPolling() {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch('/api/status');
                    const status = await response.json();
                    
                    if (!status.running) {
                        clearInterval(interval);
                        submitBtn.disabled = false;
                        
                        if (status.results) {
                            if (status.results.error) {
                                showStatus('Error: ' + status.results.error, 'error');
                            } else {
                                const downloaded = status.results.downloaded_videos?.filter(v => v.status === 'downloaded').length || 0;
                                const uploaded = status.results.uploaded_videos?.filter(v => v.status === 'uploaded').length || 0;
                                showStatus(`Complete! Downloaded: ${downloaded}, Uploaded: ${uploaded}`, 'success');
                                
                                // Show results
                                resultsDiv.innerHTML = `
                                    <h3>Results Summary</h3>
                                    <p><strong>Downloaded:</strong> ${downloaded} videos</p>
                                    <p><strong>Uploaded:</strong> ${uploaded} videos</p>
                                `;
                                resultsDiv.style.display = 'block';
                            }
                        }
                    } else {
                        showStatus(`Status: ${status.progress?.status || 'processing'}...`, 'info');
                    }
                } catch (error) {
                    console.error('Polling error:', error);
                }
            }, 2000);
        }
    </script>
</body>
</html>"""
    
    with open(template_file, 'w') as f:
        f.write(html_content)


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Create simple HTML template if it doesn't exist
    template_file = templates_dir / "index.html"
    if not template_file.exists():
        create_html_template(template_file)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
