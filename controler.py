import pandas as pd
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import requests
import io
from collections import OrderedDict
from datetime import datetime

app = Flask(__name__)
CORS(app)


######
import schedule
import time
import threading
import requests
from pytz import timezone
import subprocess

# Function to request the /last_row endpoint
def run_auto():
    subprocess.run(["python", "auto.py"])
    #subprocess.run(["hypercorn", "-w", "1", "-b", "0.0.0.0:6000", "--reload", "auto:app"])
    print("Starting Auto Outstanding...")

# Define your desired timezone
desired_timezone = "Asia/Bangkok"  # For example, New York timezone

# Schedule the task to run every day at 08:00 AM in the desired timezone
schedule.every().day.at("08:50").do(run_auto).tag('run auto').timezone = timezone(desired_timezone)

#schedule.every().day.at("01:25").do(run_auto).tag('run auto').timezone = timezone(desired_timezone)

# Function to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(4)  # Sleep for 1 second before checking the schedule again

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5200)
