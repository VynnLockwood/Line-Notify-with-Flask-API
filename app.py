
from typing import Union

from fastapi import FastAPI, HTTPException
from flask import Flask, jsonify, render_template
import pandas as pd

import mysql.connector
import requests
import yfinance as yf
from collections import OrderedDict
from datetime import datetime
import csv
import json

app = Flask(__name__)

#token = '647EdJ0GwJfNQTVb2Zf3Cgj0Xubgrb0xFAwhOxDxb5W'

#test_outstanding
token = 'GT6NcPItY171L8SiUgygR2um97L2RFeVxVFPJSuBIUD'
message = 'This is a test notification from Python!'

def get_db_connection():
    conn = mysql.connector.connect( 
            host="ideatrade.serveftp.net", 
            user="Chaluemwut@off", 
            password="NpokG70]*APxXICy", 
            port=51410, 
            database="db_ideatrade")
    return conn



# Replace 'YOUR_TOKEN_HERE' with your actual Line Notify token

#send_line_notification(message, token)
result = {}  # Define result globally
symbols = []
current_price = []
result_for_outstanding = []
report_date = []

global new_date

def fetch_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    sql_query = "SELECT DISTINCT Symbol FROM db_ideatrade.outstanding_short_positions ORDER BY Symbol ASC"
    cursor.execute(sql_query)

    unique_symbols = [row['Symbol'] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    for symbol in unique_symbols:
        result[symbol] = []

    for symbol in unique_symbols:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        sql_query = "SELECT * FROM db_ideatrade.outstanding_short_positions WHERE Symbol = %s ORDER BY Symbol ASC"
        cursor.execute(sql_query, (symbol,))

        result[symbol] = cursor.fetchall()

        cursor.close()
        conn.close()

# Function to calculate the difference between last two values of "Outstanding" for each symbol
def calculate_difference(data):
    result = {}
    for symbol, values in data.items():
        if len(symbol) <= 12:  # Check if the length of symbol is less than or equal to 12 characters
            if len(values) >= 2:
                try:
                    last_value = int(values[-1]["Outstanding"].replace(",", ""))
                    second_last_value = int(values[-2]["Outstanding"].replace(",", ""))
                    difference = last_value - second_last_value
                    if difference != "N/A":  # Check if the difference is not "N/A"
                        result[symbol] = difference

                        # Store dates of last and second last rows
                        last_date = values[-1]["date"]
                        second_last_date = values[-2]["date"]
                        if len(report_date) < 2:
                            report_date.append(second_last_date)
                            report_date.append(last_date)

                        
                except ValueError:
                    pass  # Ignore symbols with ValueError
    return result



# Function to save data to CSV file
# Function to save data to CSV file
def save_to_csv_outstanding(data_list, filename):
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["symbol", "difference"])
            writer.writeheader()
            writer.writerows(data_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Function to read data from CSV file
def read_csv(filename):
    data = []
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def graceful_shutdown(signum, frame):
    # Perform cleanup tasks or shutdown procedures here
    print("Shutting down gracefully...")

# Register the signal handler for shutdown signals


@app.get("/fetch/outstanding")
def fetch_outstanding():

# Fetch data when the application starts
    fetch_data()
    return result

@app.get("/is_new/outstanding")
def is_new_outstanding():
    global new_date

    # Check if the log.csv file exists
    if os.path.exists("log.csv"):
        # Read the last line of the file to get the last date
        with open("log.csv", "r") as file:
            lines = file.readlines()
            if lines:  # If the file is not empty
                print('log.csv is not empty')
                last_log_date = pd.to_datetime(lines[-1].strip())
            else:  # If the file is empty
                print('log.csv is empty')
                last_log_date = None
    else:
        # If log.csv doesn't exist, consider it as the first time
        print('log.csv does not exist')
        last_log_date = None

    # Get the latest date from the result data
    latest_date = max(pd.to_datetime(entry['date'], format="%d/%m/%Y") for symbol_data in result.values() for entry in symbol_data)

    # Check if it's the first time or if the latest date is newer than the date in log.csv
    if last_log_date is None or latest_date > last_log_date:
        # Update the log.csv file with the latest date
        with open("log.csv", "a") as file:
            file.write(latest_date.strftime("%Y-%m-%d %H:%M:%S") + "\n")
        message = "Data is newer. Proceeding with the app."
        new_date = True
        print(new_date)
    else:
        message = "Data is not newer. Skipping the app."
        new_date = False  # Set new_date to False if log.csv is not empty
        print(new_date)
        os.kill(os.getpid(), 9)

    return jsonify({"message": message})







@app.get("/show/outstanding")
def show_outstanding():
        return result
    
@app.get("/cal/outstanding/diff")
def get_outstanding():
    try:
        # Retrieve data
        #data = result  # Replace 'result' with your own data
        
        # Calculate difference
        difference_data = calculate_difference(result)
        
        # Convert difference_data to list of dictionaries
        data_list = [{"symbol": symbol, "difference": difference} for symbol, difference in difference_data.items()]
        
        print("This is date data: ", report_date)
        # Save difference_data to CSV file
        save_to_csv_outstanding(data_list, "outstanding_difference.csv")
        
        return difference_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/symbols")
def get_symbols():
    # Read the symbols from the outstanding_difference.csv file
    outstanding_difference_df = pd.read_csv("outstanding_difference.csv")
    
    # Extract symbols with length <= 12 characters
    symbols_list = outstanding_difference_df['symbol'].tolist()
    symbols = [symbol + ".BK" for symbol in symbols_list if len(symbol) <= 12]
    
    print(len(symbols))
    return symbols



# Function to get stock value for a symbol
def get_stock_value(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        current_value = stock.history(period="1d")['Close'].iloc[-1]
        # Round the current_value to two decimal places
        rounded_value = round(current_value, 2)
        return {"symbol": symbol, "current_value": rounded_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Function to save data to CSV file
def save_to_csv(values):
    with open('stock_values.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["symbol", "current_value"])
        writer.writeheader()
        writer.writerows(values)

# Get symbols and fetch stock value for each symbol
@app.get("/values")
def get_values():
    try:

        outstanding_difference_df = pd.read_csv("outstanding_difference.csv")
    
        # Extract symbols with length <= 12 characters
        symbols_list = outstanding_difference_df['symbol'].tolist()
        symbols = [symbol + ".BK" for symbol in symbols_list if len(symbol) <= 12]
        
        # Array to store stock values
        values = []

        # Fetch stock value for each symbol
        for symbol in symbols:
            try:
                value = get_stock_value(symbol)
                values.append(value)
            except Exception as e:
                print(f"Failed to fetch value for symbol {symbol}: {e}")
        
        # Save values to CSV
        save_to_csv(values)
        print(len(values))
        return values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cal/outstanding/mult")
def cal_values():
    outstanding_difference_df = pd.read_csv("outstanding_difference.csv")
    stock_values_df = pd.read_csv("stock_values.csv")


    # Convert 'difference' and 'current_value' columns to numeric
    outstanding_difference_df['difference'] = pd.to_numeric(outstanding_difference_df['difference'], errors='coerce')
    stock_values_df['current_value'] = pd.to_numeric(stock_values_df['current_value'], errors='coerce')

    # Calculate the product of 'difference' and 'current_value' columns
    outstanding_difference_df['calculation'] = outstanding_difference_df['difference'] * stock_values_df['current_value']

    # Select required columns for the result
    result_df = outstanding_difference_df[['symbol', 'calculation']]

    # Save the result to a new CSV file
    result_df.to_csv("calculation_result.csv", index=False)
    return jsonify(result_df.to_json()) 
#### calculation

# Read CSV files into DataFrames



##### Merge data
# Read CSV files into DataFrames

@app.get("/merge_data")
def merge_data():
    calculation_result_to_merge_df = pd.read_csv("calculation_result.csv")
    outstanding_difference_to_merge__df = pd.read_csv("outstanding_difference.csv")

    # Merge DataFrames on 'symbol' column
    merged_df = pd.merge(outstanding_difference_to_merge__df, calculation_result_to_merge_df, on='symbol', how='left')

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv("cleaned_data.csv", index=False)


    #### prepare data to send
    # Read the cleaned data from the CSV file
    cleaned_data_df = pd.read_csv("cleaned_data.csv")

    # Split data into two groups based on calculation value
    positive_data = cleaned_data_df[cleaned_data_df['calculation'] > 0]
    negative_data = cleaned_data_df[cleaned_data_df['calculation'] < 0]

    # Sort data in descending order
    positive_data_sorted = positive_data.sort_values(by='calculation', ascending=False)

    negative_data_sorted = negative_data.sort_values(by='calculation', ascending=False)


    # Save sorted data to new CSV files
    positive_data_sorted.to_csv("positive_data.csv", index=False)
    negative_data_sorted.to_csv("negative_data.csv", index=False)


    return 'data merge !'




# Define a function to apply 'k', 'm', and 'b' notation
def apply_notation(value):
    if abs(value) >= 1000000000:  # If absolute value is greater than or equal to 1 billion
        # Convert to billions with three decimal places and append 'b'
        return "{:.3f}b".format(value / 1000000000)
    elif abs(value) >= 1000000:  # If absolute value is greater than or equal to 1 million
        # Convert to millions with one decimal place and append 'm'
        return "{:.1f}m".format(value / 1000000)
    elif abs(value) >= 1000:  # If absolute value is greater than or equal to 1 thousand
        # Convert to thousands with one decimal place and append 'k'
        return "{:.1f}k".format(value / 1000)
    else:
        return str(value)  # Return the original value


####### format message
data_for_report =''
neg_data_for_report =''
global max_rows

global data1, data2, data3, data4, data5, data1_neg, data2_neg, data3_neg, data4_neg, data5_neg
vars_with_data = []
no_data_vars = []

vars_with_data_neg = []
no_data_vars_neg = []

@app.get("/format_data")
def format_data():
    global data1, data2, data3, data4, data5, data1_neg, data2_neg, data3_neg, data4_neg, data5_neg, max_rows

    greater_data = pd.read_csv("positive_data.csv")
    lower_data = pd.read_csv("negative_data.csv")

    greater_data['index'] = greater_data.index + 1
    lower_data['index'] = lower_data.index + 1

    # Extract the last column
    last_column = greater_data.iloc[:, -1]
    last_column_neg = lower_data.iloc[:, -1]

    # Reorder the remaining columns
    other_columns = greater_data.iloc[:, :-1]
    other_columns_neg = lower_data.iloc[:, :-1]

    # Concatenate the last column at the beginning
    greater_data_reordered = pd.concat([last_column, other_columns], axis=1)
    lower_data_reordered = pd.concat([last_column_neg, other_columns_neg], axis=1)

    # Rename the existing index column to 'index' and start indexing from 1
    greater_data_reordered.index = range(1, len(greater_data_reordered) + 1)
    lower_data_reordered.index = range(1, len(lower_data_reordered) + 1)

    ###### ทำ

    # Convert the 'calculation' column to integers
    greater_data_reordered['calculation'] = greater_data_reordered['calculation'].astype(float)
    lower_data_reordered['calculation'] = lower_data_reordered['calculation'].astype(float)

    # Apply the notation to the 'calculation' column
    greater_data_reordered['calculation'] = greater_data_reordered['calculation'].apply(apply_notation)
    greater_data_reordered['difference'] = greater_data_reordered['difference'].apply(apply_notation)

    lower_data_reordered['calculation'] = lower_data_reordered['calculation'].apply(apply_notation)
    lower_data_reordered['difference'] = lower_data_reordered['difference'].apply(apply_notation)

    # Store the modified DataFrame in a new variable
    data_for_report = greater_data_reordered.copy()
    neg_data_for_report = lower_data_reordered.copy()

    ####### split data for show report

    # Determine the number of splits needed
    num_splits = (len(data_for_report) + 99) // 100

    # Split the DataFrame into chunks of 100 rows each
    split_data_reports = [data_for_report[i*100:(i+1)*100] for i in range(num_splits)]
    split_data_reports_neg = [neg_data_for_report[i*100:(i+1)*100] for i in range(num_splits)]
    # Assign names to the split DataFrames, filling with "no_data" if needed
    #for positive data
    try:
        split_data_report1, split_data_report2, split_data_report3, split_data_report4, split_data_report5 = split_data_reports[:5]
    except ValueError:
        # If not enough values to unpack, fill the remaining variables with "no_data"
        split_data_report1, split_data_report2, split_data_report3, split_data_report4, split_data_report5 = split_data_reports + ["no_data"] * (5 - len(split_data_reports))

    #### check available data
    # Initialize empty lists to store variables with and without data
    

    #for negative data

    try:
        split_data_report1_neg, split_data_report2_neg, split_data_report3_neg, split_data_report4_neg, split_data_report5_neg = split_data_reports_neg[:5]
    except ValueError:
        # If not enough values to unpack, fill the remaining variables with "no_data"
        split_data_report1_neg, split_data_report2_neg, split_data_report3_neg, split_data_report4_neg, split_data_report5_neg = split_data_reports_neg + ["no_data"] * (5 - len(split_data_reports_neg))

    #### check available data
    # Initialize empty lists to store variables with and without data
    


    # Check and convert split_data_report1 to NumPy array if it contains valid data #### Positive data
    if isinstance(split_data_report1, pd.DataFrame) and not split_data_report1.empty:
        data1 = split_data_report1.to_numpy()
        vars_with_data.append('split_data_report1')
    else:
        no_data_vars.append('split_data_report1')

    # Repeat the process for other variables
    # Check and convert split_data_report2
    if isinstance(split_data_report2, pd.DataFrame) and not split_data_report2.empty:
        data2 = split_data_report2.to_numpy()
        vars_with_data.append('split_data_report2')
    else:
        no_data_vars.append('split_data_report2')

    # Check and convert split_data_report3
    if isinstance(split_data_report3, pd.DataFrame) and not split_data_report3.empty:
        data3 = split_data_report3.to_numpy()
        vars_with_data.append('split_data_report3')
    else:
        no_data_vars.append('split_data_report3')

    # Check and convert split_data_report4
    if isinstance(split_data_report4, pd.DataFrame) and not split_data_report4.empty:
        data4 = split_data_report4.to_numpy()
        vars_with_data.append('split_data_report4')
    else:
        no_data_vars.append('split_data_report4')

    # Check and convert split_data_report5
    if isinstance(split_data_report5, pd.DataFrame) and not split_data_report5.empty:
        data5 = split_data_report5.to_numpy()
        vars_with_data.append('split_data_report5')
    else:
        no_data_vars.append('split_data_report5')



    # Check and convert split_data_report1 to NumPy array if it contains valid data #### Negative data
    if isinstance(split_data_report1_neg, pd.DataFrame) and not split_data_report1_neg.empty:
        data1_neg = split_data_report1_neg.to_numpy()
        vars_with_data_neg.append('split_data_report1_neg')
    else:
        no_data_vars_neg.append('split_data_report1_neg')

    # Repeat the process for other variables
    # Check and convert split_data_report2
    if isinstance(split_data_report2_neg, pd.DataFrame) and not split_data_report2_neg.empty:
        data2_neg = split_data_report2_neg.to_numpy()
        vars_with_data_neg.append('split_data_report2_neg')
    else:
        no_data_vars_neg.append('split_data_report2_neg')

    # Check and convert split_data_report3
    if isinstance(split_data_report3_neg, pd.DataFrame) and not split_data_report3_neg.empty:
        data3_neg = split_data_report3_neg.to_numpy()
        vars_with_data_neg.append('split_data_report3_neg')
    else:
        no_data_vars_neg.append('split_data_report3_neg')

    # Check and convert split_data_report4
    if isinstance(split_data_report4_neg, pd.DataFrame) and not split_data_report4_neg.empty:
        data4_neg = split_data_report4_neg.to_numpy()
        vars_with_data_neg.append('split_data_report4_neg')
    else:
        no_data_vars_neg.append('split_data_report4_neg')

    # Check and convert split_data_report5
    if isinstance(split_data_report5_neg, pd.DataFrame) and not split_data_report5_neg.empty:
        data5_neg = split_data_report5_neg.to_numpy()
        vars_with_data_neg.append('split_data_report5_neg')
    else:
        no_data_vars_neg.append('split_data_report5_neg')

    # Print variables with and without data
    print("Variables with data:", vars_with_data)
    print("Variables without data:", no_data_vars)

    print("Neg Variables with data:", vars_with_data_neg)
    print("Neg Variables without data:", no_data_vars_neg)

    max_rows = len(data1)
    return 'formatted data !'







# Calculate the maximum number of rows

@app.get("/data_report1")
def data_report():
    global data1
    return render_template("data_report.html",data1=data1, max_rows=max_rows, report_date=report_date)

@app.get("/data_report2")
def data_report2():
    global data2
    return render_template("data_report2.html",data2=data2, max_rows=max_rows, report_date=report_date)

@app.get("/data_report3")
def data_report3():
    global data3
    return render_template("data_report3.html",data3=data3, max_rows=max_rows, report_date=report_date)

@app.get("/data_report4")
def data_report4():
    global data4
    return render_template("data_report4.html",data4=data4, max_rows=max_rows, report_date=report_date)

@app.get("/data_report5")
def data_report5():
    global data5
    return render_template("data_report5.html",data5=data5, max_rows=max_rows, report_date=report_date)

@app.get("/neg_data_report1")
def neg_data_report1():
    global data1_neg
    return render_template("neg_data_report.html",data1=data1_neg, max_rows=max_rows, report_date=report_date)

@app.get("/neg_data_report2")
def neg_data_report2():
    global data2_neg
    return render_template("neg_data_report2.html",data2=data2_neg, max_rows=max_rows, report_date=report_date)

@app.get("/neg_data_report3")
def neg_data_report3():
    global data3_neg
    return render_template("neg_data_report3.html",data3=data3_neg, max_rows=max_rows, report_date=report_date)

@app.get("/neg_data_report4")
def neg_data_report4():
    global data4_neg
    return render_template("neg_data_report4.html",data4=data4_neg, max_rows=max_rows, report_date=report_date)

@app.get("/neg_data_report5")
def neg_data_report5():
    global data5_neg
    return render_template("neg_data_report5.html",data5=data5_neg, max_rows=max_rows, report_date=report_date)




##### Test cap picture
#from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def capture(vars_with_data, vars_with_data_neg):
    # Initialize Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--window-size=2980,3119")  # Set window size

    # Initialize a WebDriver instance with Chrome options
    driver = webdriver.Chrome(options=chrome_options)

    # Capture screenshots for variables with data
    for var_name in vars_with_data:
        # Extract the last letter of the variable name
        data_number = var_name[-1]
        
        # Navigate to the webpage with the corresponding data number
        url = f'http://127.0.0.1:5002/data_report{data_number}'
        driver.get(url)

        # Wait for the page to fully load (you can adjust the sleep duration as needed)
        time.sleep(2)  # Wait for 2 seconds

        # Take a screenshot of the entire webpage
        screenshot_name = f'webpage_screenshot_{data_number}.png'
        driver.save_screenshot(screenshot_name)

    # Capture screenshots for variables with negative data
    for var_name_neg in vars_with_data_neg:
        # Extract the last letter of the variable name
        data_number_neg = var_name_neg[-5]  # Extract the last part after underscore
        
        # Navigate to the webpage with the corresponding data number for negative data
        url_neg = f'http://127.0.0.1:5002/neg_data_report{data_number_neg}'
        driver.get(url_neg)

        # Wait for the page to fully load (you can adjust the sleep duration as needed)
        time.sleep(2)  # Wait for 2 seconds

        # Take a screenshot of the entire webpage for negative data
        screenshot_name_neg = f'neg_webpage_screenshot_{data_number_neg}.png'
        driver.save_screenshot(screenshot_name_neg)

    # Quit the WebDriver
    driver.quit()

@app.get("/take_screenshot")
def take_screenshot():
    # Fetch data when the application starts
    capture(vars_with_data, vars_with_data_neg)
    return "Capture success!"




from imgurpython import ImgurClient
import os

# Initialize Imgur client with your client ID and client secret
client_id = 'de5cd6c5436730a'
client_secret = 'a8e22188bc5c878a046327aaeee79b8bf75dd119'
client = ImgurClient(client_id, client_secret)

# List of image paths to upload
#image_paths = ['webpage_screenshot_1.png', 'webpage_screenshot_2.png', 'webpage_screenshot_3.png']

image_paths = []


# Check if each file exists before adding it to the list
for filename in ['webpage_screenshot_1.png', 'webpage_screenshot_2.png', 'webpage_screenshot_3.png','webpage_screenshot_4.png', 'neg_webpage_screenshot_1.png','neg_webpage_screenshot_2.png','neg_webpage_screenshot_3.png','neg_webpage_screenshot_4.png','neg_webpage_screenshot_5.png']:
    if os.path.exists(filename):
        image_paths.append(filename)
    else:
        print(f"File '{filename}' does not exist.")

# Now 'image_paths' contains only the paths of existing image files
print("Existing image paths:", image_paths)

import os

global image_paths_list

@app.route("/refresh_images")
def refresh_images():
    image_paths = set()  # Initialize a set to store unique filenames
    global image_paths_list
    for filename in ['webpage_screenshot_1.png', 'webpage_screenshot_2.png', 'webpage_screenshot_3.png', 'webpage_screenshot_4.png', 'neg_webpage_screenshot_1.png', 'neg_webpage_screenshot_2.png', 'neg_webpage_screenshot_3.png', 'neg_webpage_screenshot_4.png', 'neg_webpage_screenshot_5.png']:
        if os.path.exists(filename):
            if filename not in image_paths:  # Check if filename is not already in the set
                image_paths.add(filename)  # Add the filename to the set
            else:
                print(f"File '{filename}' already exists in the image paths.")
        else:
            print(f"File '{filename}' does not exist.")

    # Sort the list to ensure webpage files come before neg_webpage files
    image_paths_list = sorted(image_paths, key=lambda x: (not x.startswith('webpage'), x))
    print("Existing image paths:", image_paths_list)
    return {"get new images": image_paths_list} 


#image_paths = ['webpage_screenshot_1.png']

# Endpoint to delete existing image files
@app.route("/delete_existing_images")
def delete_existing_images():
    deleted_files = []
    for path in image_paths:
        if os.path.exists(path):
            os.remove(path)
            deleted_files.append(path)
    return {"message": f"Deleted {len(deleted_files)} existing image files", "deleted_files": deleted_files}

# List to store the uploaded image URLs
uploaded_image_urls = []

# Function to upload screenshots and store their URLs
def upload_screenshots(image_paths):
    global image_paths_list
    for image_path in image_paths:
        # Upload each image
        uploaded_image = client.upload_from_path(image_path, config=None, anon=True)
        # Store the URL of the uploaded image
        uploaded_image_urls.append(uploaded_image['link'])
        # Print the uploaded image's URL (optional)
        print("Uploaded image URL:", uploaded_image['link'])
    return "Upload success!"


# Access the list of uploaded image URLs
#print("Uploaded image URLs:", uploaded_image_urls)
#print("Image paths : ", image_paths)

@app.get("/upload_screenshot")
def upload_screenshot():
    # Fetch data when the application starts
    upload_screenshots(image_paths_list)
    return "Upload success!"
##### get rank for each data



######### send data to line notify

import requests
def send_line_notification_with_images(message, image_urls, token, positive_data_ranges, negative_data_ranges):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ' + token
    }

    # Merge positive and negative data ranges
    all_data_ranges = positive_data_ranges + negative_data_ranges

    # Ensure number of notifications matches number of images
    num_notifications = min(len(all_data_ranges), len(image_urls))

    # Send notifications
    for i in range(num_notifications):
        data_range = all_data_ranges[i]
        image_url = image_urls[i]
        is_positive = i < len(positive_data_ranges)
        data_type = "รายชื่อหุ้นที่มี Outstanding เพิ่มขึ้น" if is_positive else "รายชื่อหุ้นที่มี Outstanding ลดลง"
        message_with_range = f"{message}\n\n{data_type} ข้อมูลลำดับที่ : {data_range}"
        send_message_and_image(url, headers, message_with_range, image_url, data_range)

def send_message_and_image(url, headers, message, image_url, data_range):
    data = {'message': message, 'imageThumbnail': image_url, 'imageFullsize': image_url}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print(f"Notification for {data_range} sent successfully!")
    else:
        print(f"Failed to send notification for {data_range}. Status code:", response.status_code)

# Example usage
message = "มาดูรายชื่อหุ้นที่มี Outstanding เปลี่ยนแปลงกัน!"

print(uploaded_image_urls)

positive_data_ranges = []
negative_data_ranges = []

@app.route("/get_data_range")
def get_data_range():
    # Load positive_data.csv and negative_data.csv to get the number of rows
    positive_data = pd.read_csv("positive_data.csv")
    negative_data = pd.read_csv("negative_data.csv")

    # Calculate the number of splits needed for positive_data.csv
    num_splits_positive = (len(positive_data) + 99) // 100

    # Calculate the number of splits needed for negative_data.csv
    num_splits_negative = (len(negative_data) + 99) // 100

    # Initialize lists to store data ranges for positive and negative data
    

    # Calculate data ranges for positive_data.csv
    for i in range(num_splits_positive):
        start_row = i * 100 + 1
        end_row = min((i + 1) * 100, len(positive_data))
        data_range = f"{start_row}-{end_row}"
        positive_data_ranges.append(data_range)

    # Calculate data ranges for negative_data.csv
    for i in range(num_splits_negative):
        start_row = i * 100 + 1
        end_row = min((i + 1) * 100, len(negative_data))
        data_range = f"{start_row}-{end_row}"
        negative_data_ranges.append(data_range)

    print(positive_data_ranges)
    print(negative_data_ranges)
    return "get data range!"



import sys
import subprocess
# Function to reload the application

import psutil

def kill_process(process_name):
    # Iterate over all running processes
    for proc in psutil.process_iter():
        try:
            # Check if the process name matches the target process name
            if proc.name() == process_name:
                # Terminate the process
                proc.terminate()
                return True  # Process terminated successfully
        except psutil.NoSuchProcess:
            # Ignore processes that no longer exist
            pass
    return False  # Process not found


def start_new_process(script_path):
    # Start a new Python process for the specified script
    subprocess.Popen(['python', script_path])

@app.route('/restart_process', methods=['GET'])
def restart_process():
    # Kill the existing Python process with the specified name
    process_name = "app.py"
    kill_process(process_name)
    
    # Wait for the process to terminate
    time.sleep(2)  # Adjust the sleep duration as needed
    
    # Start a new Python process with the specified script path
    script_path = "app.py"
    start_new_process(script_path)
    
    return jsonify(message="Process restarted successfully")


@app.get("/send_line_notification")
def send_line_notification():

# Fetch data when the application starts
    #send_line_notification_with_images(message, uploaded_image_urls, token)
    send_line_notification_with_images(message, uploaded_image_urls, token, positive_data_ranges, negative_data_ranges)
    return "Notify to line success!"

import os
import sys
from flask import request

# Terminate the current Python process
'''
@app.route('/kill_itself')
def kill_itself():
    # Perform any cleanup operations here...
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func:
        shutdown_func()
        return jsonify(message="Server shutting down..."), 200
    else:
        return jsonify(message="Shutdown function not available"), 500
'''
import signal

shutdown_in_progress = False

def cleanup():
    # Perform cleanup tasks here (e.g., close database connections)
    print("Performing cleanup tasks...")
    # Add any cleanup tasks here...

def graceful_shutdown(signum, frame):
    global shutdown_in_progress
    if not shutdown_in_progress:
        print("Received signal for graceful shutdown")
        shutdown_in_progress = True
        cleanup()
        sys.exit(0)
    else:
        print("Shutdown already in progress, ignoring signal")

@app.route('/shutdown')
def shutdown():
    print('success shutdown app !')
    os.kill(os.getpid(), 9)
    return jsonify(message="Shutdown app"), 400
    

####### Auto
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        filename = os.path.basename(event.src_path)
        if filename.endswith('.csv'):
            # Update CSV file in your Flask application
            pass
        elif filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # Update image file in your Flask application
            pass

def start_file_monitor():
    observer = Observer()
    observer.schedule(FileChangeHandler(), path='./', recursive=True)
    observer.start()
    try:
        while True:
            # Your Flask application runs here
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    app.run(debug=False, port=5002)
    start_file_monitor()
    