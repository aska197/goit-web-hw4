from flask import Flask, render_template, request, url_for, redirect
from datetime import datetime
import socket
import json
import os
from threading import Thread

app = Flask(__name__)

# Function to save a message to data.json
def save_message(username, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    new_message = {
        timestamp: {
            "username": username,
            "message": message,
            "timestamp": timestamp
        }
    }

    # Load existing data from the file if it exists
    data_file = os.path.join('storage', 'data.json')
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []

        # Append the new message to the existing data
        existing_data.append(new_message)
    else:
        existing_data = [new_message]

    # Write the updated data back to the file
    with open(data_file, 'w') as f:
        json.dump(existing_data, f, indent=4)

# Route for index.html
@app.route('/')
def index():
    return render_template('index.html')

# Route for message.html
@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message_text = request.form['message']
        
        # Save the message to data.json
        save_message(username, message_text)

        # Redirect to the index page after processing the message
        return redirect(url_for('index'))

    # Render message.html with necessary CSS and JS references
    return render_template('message.html', css_url=url_for('static', filename='style.css'))

# Route for handling 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

# Set up UDP socket server
UDP_IP = '127.0.0.1'
UDP_PORT = 5000

# Function to handle UDP messages
def udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    while True:
        data, _ = sock.recvfrom(1024)
        try:
            message_data = json.loads(data)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            message_data['timestamp'] = timestamp

            # Save message to data.json file
            storage_dir = 'storage'
            if not os.path.exists(storage_dir):
                os.makedirs(storage_dir)
            with open(os.path.join(storage_dir, 'data.json'), 'a+') as f:
                json.dump({timestamp: message_data}, f)
                f.write('\n')

        except Exception as e:
            print('Error processing message:', e)

if __name__ == '__main__':
    # Start UDP server in a separate thread
    udp_thread = Thread(target=udp_server)
    udp_thread.daemon = True
    udp_thread.start()

    # Start Flask HTTP server
    app.run(port=3000)
