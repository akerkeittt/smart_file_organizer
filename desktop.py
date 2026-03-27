"""
Smart File Organizer — Desktop Wrapper
Launches the Flask backend internally and wraps the UI inside a native Windows Edge WebView context.
"""

import sys
import logging
import threading
import time
import webview
from app import app

def start_server():
    # Hide verbose Flask Werkzeug logs during desktop operation
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(port=5055, use_reloader=False)

if __name__ == '__main__':
    print("Initializing Smart File Organizer Desktop Environment...")
    
    # 1. Start Flask API + React Host in background thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Delay quickly to ensure Flask socket binds
    time.sleep(1)
    
    print("Launching Native Window...")
    
    # 2. Spawn native OS Window rendering localhost
    webview.create_window(
        title='Smart File Organizer',
        url='http://localhost:5055/',
        width=1280,
        height=850,
        min_size=(800, 600)
    )
    
    webview.start()
    
    # 3. Terminate background threads when User closes the Window
    sys.exit()
