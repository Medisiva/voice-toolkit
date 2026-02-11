#!/usr/bin/env python3
"""
Simple server for Voice Claude web interface.

Receives transcribed text from browser, sends to Claude Code, returns response.
"""

import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os

PORT = 8096


class VoiceClaudeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve files from the web_voice directory
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            self.handle_chat()
        else:
            self.send_error(404)

    def handle_chat(self):
        # Read request
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        message = data.get('message', '')
        cwd = data.get('cwd', os.getcwd())

        print(f"\n>>> User: {message}")
        print(f"    CWD: {cwd}")

        # Send to Claude Code
        try:
            result = subprocess.run(
                ["claude", "-p", "--continue", message],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            response = result.stdout.strip()
            if not response and result.stderr:
                response = f"Error: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            response = "Claude took too long to respond."
        except Exception as e:
            response = f"Error: {e}"

        print(f"<<< Claude: {response[:100]}...")

        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        self.wfile.write(json.dumps({'response': response}).encode())


def main():
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  Voice Claude Server                                      ║
╠══════════════════════════════════════════════════════════╣
║  Open in Chrome: http://localhost:{PORT}                   ║
║                                                           ║
║  • Click the mic button or press Space                    ║
║  • Speak your command                                     ║
║  • Claude will respond                                    ║
║                                                           ║
║  Press Ctrl+C to stop                                     ║
╚══════════════════════════════════════════════════════════╝
""")

    server = HTTPServer(('', PORT), VoiceClaudeHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
