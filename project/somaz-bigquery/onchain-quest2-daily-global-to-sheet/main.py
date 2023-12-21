import os
import requests
import datetime
import gspread
from google.oauth2.service_account import Credentials
from flask import jsonify
import time

# Make sure to set 'DUNE_API_KEY' and 'SHEET_ID' in your environment variables.

def get_yesterdays_date_utc():
    # Get the current time in UTC and then subtract one day
    utc_now = datetime.datetime.utcnow()
    yesterdays_date_utc = utc_now - datetime.timedelta(days=1)
    return yesterdays_date_utc.strftime('%Y-%m-%d')

def fetch_data_from_dune():
    API_KEY = os.getenv('DUNE_API_KEY')
    DAILY_QUERY_ID = '2320785'  # Replace with your actual query ID
    GLOBAL_QUERY_ID = '2418373'

    headers = {
        "Content-Type": "application/json",
        "X-Dune-API-Key": API_KEY
    }

    payload = {
        "parameters": [
            {
                "key": "date",
                "value": get_yesterdays_date_utc(),
                "type": "datetime"
            }
        ]
    }

    # Function to execute a query and return results
    def execute_query(query_id):
        execute_endpoint = f"https://api.dune.com/api/v1/query/{query_id}/execute"
        execute_response = requests.post(execute_endpoint, json=payload, headers=headers)
        if execute_response.status_code != 200:
            print(f"Error executing query: {execute_response.text}")
            return None

        execution_id = execute_response.json()["execution_id"]

        # Check the status of the query execution
        status_endpoint = f"https://api.dune.com/api/v1/execution/{execution_id}/status"
        while True:
            status_response = requests.get(status_endpoint, headers=headers)
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data["state"] == "QUERY_STATE_COMPLETED":
                    results_endpoint = f"https://api.dune.com/api/v1/execution/{execution_id}/results"
                    results_response = requests.get(results_endpoint, headers=headers)
                    if results_response.status_code == 200:
                        result_data = results_response.json()
                        if "result" in result_data and "rows" in result_data["result"]:
                            return result_data["result"]["rows"]
                    break
            time.sleep(5)

        return None

    # Execute both queries
    daily_data = execute_query(DAILY_QUERY_ID)
    global_data = execute_query(GLOBAL_QUERY_ID)

    print("Daily data:", daily_data)
    print("Global data:", global_data)

    yesterdays_date = get_yesterdays_date_utc()

    def get_count_for_date(data, date):
        for row in data:
            if row.get('일자(KST)', '').startswith(date):
                return row.get('퀘스트 완료 수', 0)
        return 0

    daily_count = get_count_for_date(daily_data, yesterdays_date)
    global_count = get_count_for_date(global_data, yesterdays_date)

    print("Daily count:", daily_count)
    print("Global count:", global_count)

    if global_count > daily_count:
        return global_data
    elif daily_count > 0:
        return daily_data
    else:
        return [{'일자(KST)': yesterdays_date, '퀘스트 완료 수': 0}]

def find_row_for_date(worksheet, date):
    date_column_values = worksheet.col_values(1)
    try:
        return date_column_values.index(date) + 1
    except ValueError:
        return None

def write_to_sheet(worksheet, row_number, data):
    if row_number is None or row_number < 2:  # Ensure row_number is valid and not the first row
        print("Invalid row number in the sheet")
        return

    # Define the columns where data will be written, using the correct key names
    columns = {
        'DL': data.get('퀘스트 완료 수', 0)  
    }

    # Update cell values and apply center alignment for regular columns
    for col, value in columns.items():
        cell = f'{col}{row_number}'
        worksheet.update(cell, value)

        # Set cell format to center alignment
        worksheet.format(cell, {
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE"
        })

def main(request):
    try:
        # Fetch data from Dune Analytics
        rows = fetch_data_from_dune()
        if not rows:
            error_message = "Failed to fetch data from Dune Analytics."
            print(error_message)
            return jsonify({'error': error_message}), 500

        # Set up Google Sheets access
        SERVICE_ACCOUNT_FILE = 'bigquery.json'
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        gc = gspread.authorize(creds)
        SHEET_ID = os.getenv('SHEET_ID')
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet("Somaz_Table")

        # Get yesterday's date and find corresponding row in the sheet
        yesterdays_date = get_yesterdays_date_utc()
        row_number = find_row_for_date(worksheet, yesterdays_date)

        # Convert API date to just the date part for comparison
        for data in rows:
            # The key for the date in the data should match the actual key from the query results
            date_key = '일자(KST)' if '일자(KST)' in data else '일자'
            if date_key in data:
                api_date = data[date_key].split(' ')[0]
                if api_date == yesterdays_date: 
                    write_to_sheet(worksheet, row_number, data)
                    break
            else:
                print(f"Missing '{date_key}' key in data: {data}")

        success_message = "Data written to sheet successfully"
        print(success_message)
        return success_message, 200

    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        return jsonify({'error': error_message}), 500

