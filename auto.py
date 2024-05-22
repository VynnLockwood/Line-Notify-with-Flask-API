import pandas as pd
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import requests
import os
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

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

# Create a new instance of the Firefox driver
driver = webdriver.Chrome()

import requests
        
# Function to request the /last_row endpoint
def run_app():
    subprocess.run(["python", "app.py"])
    #subprocess.run(["hypercorn", "-w", "1", "-b", "0.0.0.0:5002", "--reload", "app:app"])
    print("Starting app...")


def fetch_new_data():
    try:
        url = 'http://127.0.0.1:5002/fetch/outstanding'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("New data fetched !")
    except Exception as e:
        print(f"Failed to fetch.: {e}")

def is_new_data():
    try:
        url = 'http://127.0.0.1:5002/is_new/outstanding'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Detect new data !")
    except Exception as e:
        print(f"Not detect new data.: {e}")


def cal_outstanding_diff():
    try:
        url = 'http://127.0.0.1:5002/cal/outstanding/diff'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Calculated outstanding different !")
    except Exception as e:
        print(f"Failed to cal outstanding.: {e}")

def apply_symbols():
    try:
        url = 'http://127.0.0.1:5002/symbols'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("applied symbols !")
    except Exception as e:
        print(f"Failed to apply symbols. !: {e}")

def get_current_value():
    try:
        url = 'http://127.0.0.1:5002/values'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Success get current value of all symbols !")
    except Exception as e:
        print(f"Failed to get current values. !: {e}")

########### hold for 5 minutes

def cal_net_value():
    
    try:
        url = 'http://127.0.0.1:5002/cal/outstanding/mult'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Success to cal outstanding mul !")
    except Exception as e:
        print(f"Failed to cal outstanding mul : {e}")

########### Refresh app to get present csv data (Kill and restart)
def merge_data():
    url = 'http://127.0.0.1:5002/merge_data'  # Replace with your server's URL
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Success merge data !")
        else:
            print(f"Failed to merge data: {response.status_code}")
    except Exception as e:
        print(f"Failed to merge data: {e}")

def format_data():
    url = 'http://127.0.0.1:5002/format_data'  # Replace with your server's URL
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Success format data !")
        else:
            print(f"Failed to format data: {response.status_code}")
    except Exception as e:
        print(f"Failed to format data: {e}")

def take_screenshot():
    try:
        url = 'http://127.0.0.1:5002/take_screenshot'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Success to take screenshot !")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")


def refresh_images():
    try:
        url = 'http://127.0.0.1:5002/refresh_images'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Success to refresh images !")
    except Exception as e:
        print(f"Failed to refresh images: {e}")


def upload_screenshot():
    try:
        url = 'http://127.0.0.1:5002/upload_screenshot'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Success to upload screenshot !")
    except Exception as e:
        print(f"Failed to upload screenshot: {e}")
    #finally:
        #driver.quit()  # Close the browser


def get_data_range():
    try:
        url = 'http://127.0.0.1:5002/get_data_range'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Success to get data range !")
    except Exception as e:
        print(f"Failed to get data range: {e}")


def send_line_notify():
    try:
        url = 'http://127.0.0.1:5002/send_line_notification'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Success to send_line_notification !")
    except Exception as e:
        print(f"Failed to send_line_notification: {e}")
    finally:
        driver.quit()  # Close the browser


def shut_app_down():
    try:
        url = 'http://127.0.0.1:5002/shutdown'  # Replace with your server's URL
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Add Selenium interactions here
        print("Success to shutdown app !")
    except Exception as e:
        print(f"Failed to shutdown app: {e}")
    finally:
        driver.quit()  # Close the browser


def shut_auto_down():
    print("Shutdown itself")
    os.kill(os.getpid(), 9)
    


# Terminate the current Python process
@app.route('/kill_itself_api')
def kill_itself_api():
    print('Shutdown auto success')
    os.kill(os.getpid(), 9)
    return jsonify(message="Shutdown app"), 400

# Terminate the current Python process
@app.get('/')
def home():
    return 'hello'

def delete_pics():
    subprocess.run(["python", "pics_delete.py"])
    #subprocess.run(["hypercorn", "-w", "1", "-b", "0.0.0.0:5002", "--reload", "app:app"])
    print("Deleted old pictures...")


# Define your desired timezone
desired_timezone = "Asia/Bangkok"  # For example, New York timezone

# Schedule the task to run every day at 08:00 AM in the desired timezone
schedule.every().day.at("09:00").do(run_app).tag('run app').timezone = timezone(desired_timezone)

schedule.every().day.at("09:05").do(fetch_new_data).tag('fetch new data').timezone = timezone(desired_timezone)

schedule.every().day.at("09:07").do(is_new_data).tag('is_new_data').timezone = timezone(desired_timezone)

schedule.every().day.at("09:08").do(cal_outstanding_diff).tag('cal outstanding diff').timezone = timezone(desired_timezone)

schedule.every().day.at("09:09").do(apply_symbols).tag('apply symbols').timezone = timezone(desired_timezone)

schedule.every().day.at("09:10").do(get_current_value).tag('get current value').timezone = timezone(desired_timezone) ## hold this

schedule.every().day.at("09:20").do(cal_net_value).tag('cal net value').timezone = timezone(desired_timezone)

##### refresh to get lasted csv data update
schedule.every().day.at("09:21").do(merge_data).tag('kill itself to refresh data').timezone = timezone(desired_timezone)

schedule.every().day.at("09:22").do(format_data).tag('run app to refresh data').timezone = timezone(desired_timezone)

schedule.every().day.at("09:23").do(take_screenshot).tag('take screenshot').timezone = timezone(desired_timezone)

##### refresh to get current data of image
schedule.every().day.at("09:25").do(refresh_images).tag('kill itself to get pics').timezone = timezone(desired_timezone)

schedule.every().day.at("09:26").do(upload_screenshot).tag('upload screeenshot').timezone = timezone(desired_timezone)

schedule.every().day.at("09:27").do(get_data_range).tag('get data range').timezone = timezone(desired_timezone)

schedule.every().day.at("09:30").do(send_line_notify).tag('send line notify').timezone = timezone(desired_timezone)

schedule.every().day.at("09:40").do(shut_app_down).tag('shut app down').timezone = timezone(desired_timezone)

schedule.every().day.at("09:42").do(delete_pics).tag('delete_pics').timezone = timezone(desired_timezone)

schedule.every().day.at("09:45").do(shut_auto_down).tag('Kill itself').timezone = timezone(desired_timezone)


"""

schedule.every().day.at("01:30").do(run_app).tag('run app').timezone = timezone(desired_timezone)

schedule.every().day.at("01:32").do(fetch_new_data).tag('fetch new data').timezone = timezone(desired_timezone)

schedule.every().day.at("01:33").do(is_new_data).tag('is_new_data').timezone = timezone(desired_timezone)

schedule.every().day.at("01:34").do(cal_outstanding_diff).tag('cal outstanding diff').timezone = timezone(desired_timezone)

#schedule.every().day.at("00:35").do(apply_symbols).tag('apply symbols').timezone = timezone(desired_timezone)

schedule.every().day.at("01:35").do(get_current_value).tag('get current value').timezone = timezone(desired_timezone) ## hold this

schedule.every().day.at("01:45").do(cal_net_value).tag('cal net value').timezone = timezone(desired_timezone)

##### refresh to get lasted csv data update
schedule.every().day.at("01:46").do(merge_data).tag('kill itself to refresh data').timezone = timezone(desired_timezone)

schedule.every().day.at("01:47").do(format_data).tag('run app to refresh data').timezone = timezone(desired_timezone)

schedule.every().day.at("01:48").do(take_screenshot).tag('take screenshot').timezone = timezone(desired_timezone)

##### refresh to get current data of image
schedule.every().day.at("01:50").do(refresh_images).tag('kill itself to get pics').timezone = timezone(desired_timezone)

schedule.every().day.at("01:52").do(upload_screenshot).tag('upload screeenshot').timezone = timezone(desired_timezone)

schedule.every().day.at("01:54").do(get_data_range).tag('get data range').timezone = timezone(desired_timezone)

schedule.every().day.at("01:55").do(send_line_notify).tag('send line notify').timezone = timezone(desired_timezone)

schedule.every().day.at("01:57").do(shut_app_down).tag('shut app down').timezone = timezone(desired_timezone)

schedule.every().day.at("01:58").do(delete_pics).tag('delete_pics').timezone = timezone(desired_timezone)

schedule.every().day.at("01:59").do(shut_auto_down).tag('Kill itself').timezone = timezone(desired_timezone)

"""


#### close app

# Function to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(4)  # Sleep for 1 second before checking the schedule again

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)
