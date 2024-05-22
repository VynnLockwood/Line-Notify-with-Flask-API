from flask import Flask, jsonify
import subprocess
import signal
import os
import time


def start_new_process(script_path):
    # Start a new Python process for the specified script
    subprocess.Popen(['python', script_path])

def restart_process():

    
    # Wait for the process to terminate
    time.sleep(2)  # Adjust the sleep duration as needed
    
    # Start a new Python process with the specified script path
    script_path = "app.py"
    start_new_process(script_path)
    
    return jsonify(message="Process restarted successfully")

restart_process()
