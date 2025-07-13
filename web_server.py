from flask import Flask, jsonify
import asyncio
import logging
from threading import Thread
import psutil
import os
from datetime import datetime

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables to store bot status
bot_status = {
    'is_online': False,
    'start_time': None,
    'guilds': 0,
    'users': 0,
    'latency': 0
}

def update_bot_status(bot=None):
    """Update bot status for web server."""
    global bot_status
    
    if bot:
        bot_status['is_online'] = True
        bot_status['guilds'] = len(bot.guilds)
        bot_status['users'] = len(bot.users)
        bot_status['latency'] = round(bot.latency * 1000, 2)
    else:
        bot_status['is_online'] = False

@app.route('/')
def home():
    """Health check endpoint."""
    return jsonify({
        'status': 'online',
        'message': 'Epic RPG Bot is running!',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Detailed health check."""
    try:
        # System stats
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate uptime
        uptime = None
        if bot_status['start_time']:
            uptime = (datetime.now() - bot_status['start_time']).total_seconds()
        
        return jsonify({
            'status': 'healthy',
            'bot': {
                'online': bot_status['is_online'],
                'guilds': bot_status['guilds'],
                'users': bot_status['users'],
                'latency': f"{bot_status['latency']}ms",
                'uptime': uptime
            },
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'python_version': os.sys.version.split()[0]
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/status')
def status():
    """Simple status endpoint."""
    return jsonify({
        'online': bot_status['is_online'],
        'guilds': bot_status['guilds'],
        'users': bot_status['users']
    })

def run_flask_app():
    """Run Flask app in a separate thread."""
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask app error: {e}")

async def start_web_server():
    """Start the web server."""
    try:
        # Update start time
        bot_status['start_time'] = datetime.now()
        
        # Start Flask in a separate thread
        flask_thread = Thread(target=run_flask_app, daemon=True)
        flask_thread.start()
        
        logger.info("✅ Web server started on port 5000")
    except Exception as e:
        logger.error(f"❌ Failed to start web server: {e}")

# Function to be called by the bot to update status
def set_bot_online(bot):
    """Set bot as online and update stats."""
    global bot_status
    bot_status['is_online'] = True
    update_bot_status(bot)

def set_bot_offline():
    """Set bot as offline."""
    global bot_status
    bot_status['is_online'] = False
    bot_status['guilds'] = 0
    bot_status['users'] = 0
    bot_status['latency'] = 0

def run_web_server():
    """Run the web server - wrapper function for compatibility."""
    try:
        # Disable Flask's default logging to reduce noise
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
        
        # Get port from environment, default to 5000
        port = int(os.getenv('PORT', 5000))
        
        logger.info(f"Starting web server on port {port}")
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")
