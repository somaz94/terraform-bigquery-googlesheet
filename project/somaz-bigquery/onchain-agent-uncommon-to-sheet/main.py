import os
import requests
import datetime
import gspread
from google.oauth2.service_account import Credentials
from flask import jsonify
import time

# Make sure to set 'DUNE_API_KEY' and 'SHEET_ID' in your environment variables.

def fetch_data_from_dune():
    API_KEY = os.getenv('DUNE_API_KEY')
    QUERY_ID = ''  # Replace with your actual query ID

    # Endpoint to execute the query
    DUNE_API_EXECUTE_ENDPOINT = f"https://api.dune.com/api/v1/query/{QUERY_ID}/execute"

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

    # Execute the query
    execute_response = requests.post(DUNE_API_EXECUTE_ENDPOINT, json=payload, headers=headers)
    if execute_response.status_code != 200:
        print(f"Error executing query: {execute_response.text}")
        return None

    execution_id = execute_response.json()["execution_id"]

    # Check the status of the query execution
    DUNE_API_STATUS_ENDPOINT = f"https://api.dune.com/api/v1/execution/{execution_id}/status"
    while True:
        status_response = requests.get(DUNE_API_STATUS_ENDPOINT, headers=headers)
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data["state"] == "QUERY_STATE_COMPLETED":
                break
            elif status_data["state"] == "QUERY_STATE_FAILED":
                print("Query execution failed.")
                return None
        time.sleep(5)  # Adjust the sleep time as needed

    # Fetch the results of the query
    DUNE_API_RESULTS_ENDPOINT = f"https://api.dune.com/api/v1/execution/{execution_id}/results"
    results_response = requests.get(DUNE_API_RESULTS_ENDPOINT, headers=headers)

    if results_response.status_code == 200:
        result_data = results_response.json()
        print("Result Data:", result_data)  # This line is for debugging

        # Check if 'result' and 'rows' keys exist in the result_data
        if "result" in result_data and "rows" in result_data["result"]:
            return result_data["result"]["rows"]
        else:
            print(f"Unexpected result structure: {result_data}")
            return None
    else:
        print(f"Error fetching query results: {results_response.text}")
        return None

def get_yesterdays_date_utc():
    # Get the current time in UTC and then subtract one day
    utc_now = datetime.datetime.utcnow()
    yesterdays_date_utc = utc_now - datetime.timedelta(days=1)
    return yesterdays_date_utc.strftime('%Y-%m-%d')

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
        'BC': data.get('민팅 수량', 0),  # Minting Quantity
        'CB': data.get('퀘스트 소각 수량', 0),  # Quest Burn Quantity
        'CG': data.get('다오 소각 수량', 0),  # Dao Burn Quantity
        # 'CQ': data.get('최고 가격(/NFT)', 0)  # Highest Price(/NFT) - Special handling below
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

    # Special handling for '최고 가격(/NFT)' column
    highest_price_cell = f'CQ{row_number}'
    highest_price = data.get('최고 가격(/NFT)')
    if highest_price is not None:
        # Update the cell as a string if there is a value
        worksheet.update(highest_price_cell, str(highest_price), value_input_option='USER_ENTERED')
    else:
        # Directly copy the value from the previous row as a string
        previous_row_value = worksheet.acell(f'CQ{row_number - 1}').value
        if previous_row_value:
            worksheet.update(highest_price_cell, previous_row_value, value_input_option='USER_ENTERED')
        else:
            print("Previous row has no value for highest price.")

    # Set cell format to center alignment for '최고 가격(/NFT)' column
    worksheet.format(highest_price_cell, {
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
            # Check if '일자' key exists in the data
            if '일자' in data:
                api_date = data['일자'].split(' ')[0]
                if api_date == yesterdays_date: 
                    write_to_sheet(worksheet, row_number, data)
                    break
            else:
                print(f"Missing '일자' key in data: {data}")

        success_message = "Data written to sheet successfully"
        print(success_message)
        return success_message, 200

    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        return jsonify({'error': error_message}), 500


