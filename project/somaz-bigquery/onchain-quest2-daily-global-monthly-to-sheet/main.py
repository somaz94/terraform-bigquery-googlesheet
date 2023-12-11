import os
import requests
import datetime
import gspread
from google.oauth2.service_account import Credentials
from flask import jsonify
import time

def fetch_data_from_dune():
    API_KEY = os.getenv('DUNE_API_KEY')
    DAILY_QUERY_ID = '' # Replace with your Dune Query ID
    GLOBAL_QUERY_ID = '' # Replace with your Dune Query ID

    headers = {
        "Content-Type": "application/json",
        "X-Dune-API-Key": API_KEY
    }

    def execute_query(query_id):
        payload = {
            "parameters": [
                # No date parameter required as we are fetching all data
            ]
        }
        execute_endpoint = f"https://api.dune.com/api/v1/query/{query_id}/execute"
        execute_response = requests.post(execute_endpoint, headers=headers, json=payload)
        if execute_response.status_code != 200:
            print(f"Error executing query: {execute_response.text}")
            return None

        execution_id = execute_response.json()["execution_id"]
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
                        return result_data["result"]["rows"]
            time.sleep(5)

    # Execute queries and return their results
    daily_data = execute_query(DAILY_QUERY_ID)
    global_data = execute_query(GLOBAL_QUERY_ID)

    return daily_data, global_data

def combine_data(daily_data, global_data):
    combined_data = {}
    for row in daily_data + global_data:
        date_key = row['일자(KST)' if '일자(KST)' in row else '일자']
        quest_completion_count = row.get('퀘스트 완료 수', 0)
        if date_key not in combined_data or combined_data[date_key] < quest_completion_count:
            combined_data[date_key] = quest_completion_count
    return combined_data

def get_yesterdays_date_utc():
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
    if row_number is None or row_number < 2:
        print("Invalid row number in the sheet")
        return

    columns = {
        'AB': data
    }

    for col, value in columns.items():
        cell = f'{col}{row_number}'
        worksheet.update(cell, value)
        worksheet.format(cell, {
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE"
        })
        time.sleep(1)


def main(request):
    try:
        daily_data, global_data = fetch_data_from_dune()
        if not (daily_data and global_data):
            error_message = "Failed to fetch data from Dune Analytics."
            print(error_message)
            return jsonify({'error': error_message}), 500

        combined_data = combine_data(daily_data, global_data)

        # Google Sheets setup
        SERVICE_ACCOUNT_FILE = 'bigquery.json'
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        gc = gspread.authorize(creds)
        SHEET_ID = os.getenv('SHEET_ID')
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet("[Quest]Daily&Global")

        # Fetch all date column values at once
        date_column_values = worksheet.col_values(1)
        
        batch_updates = []
        current_month = datetime.datetime.now().month
        for date_key, quest_completion_count in combined_data.items():
            data_month = datetime.datetime.strptime(date_key, '%Y-%m-%d').month
            if data_month != current_month:  # Only process data not from the current month
                try:
                    row_number = date_column_values.index(date_key) + 1
                    cell = f'AB{row_number}'
                    batch_updates.append({
                        'range': cell,
                        'values': [[quest_completion_count]]
                    })
                except ValueError:
                    continue  # Skip if date not found

        # Perform batch update
        if batch_updates:
            worksheet.batch_update(batch_updates)

        success_message = "Data written to sheet successfully"
        print(success_message)
        return success_message, 200

    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        return jsonify({'error': error_message}), 500
