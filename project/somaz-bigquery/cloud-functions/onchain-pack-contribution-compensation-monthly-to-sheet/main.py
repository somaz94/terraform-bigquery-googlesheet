import os
import requests
import datetime
import gspread
from google.oauth2.service_account import Credentials
import time
from flask import jsonify

def fetch_data_from_dune():
    API_KEY = os.getenv('DUNE_API_KEY')
    PACK_CONTRIBUTION_COMPENSATION_QUERY_ID = '' # Replace with your actual query ID

    headers = {
        "Content-Type": "application/json",
        "X-Dune-API-Key": API_KEY
    }

    def execute_query(query_id):
        payload = {"parameters": []}  # No parameters required
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

    return execute_query(PACK_CONTRIBUTION_COMPENSATION_QUERY_ID)

def find_row_for_date(worksheet, date):
    col_values = worksheet.col_values(1)
    for idx, val in enumerate(col_values):
        val_cleaned = val.strip()
        if val_cleaned == date:
            print(f"Date {date} found at row {idx + 1}")  # 디버깅 코드 추가
            return idx + 1  # Found the row
    print(f"Date {date} not found")  # 디버깅 코드 추가
    return None  # Date not found

def write_to_sheet(worksheet, updates):
    # Apply all updates in a single batch
    print("Applying updates:", updates)  # Debugging: print updates
    worksheet.batch_update(updates)

def main(request):
    try:
        global_data = fetch_data_from_dune()
        if not global_data:
            error_message = "Failed to fetch data from Dune Analytics."
            print(error_message)
            return jsonify({'error': error_message})

        print("Fetched data:", global_data)  # Debugging: print fetched data

        SERVICE_ACCOUNT_FILE = 'bigquery.json'
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        gc = gspread.authorize(creds)
        SHEET_ID = os.getenv('SHEET_ID')
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet("Somaz_Table(Pack)")

        updates = []  # Initialize an empty list for batch updates
        for row in global_data:
            date_key = datetime.datetime.strptime(row['일자'], '%Y-%m-%d').strftime('%Y-%m-%d')
            row_number = find_row_for_date(worksheet, date_key)
            if row_number is not None:
                # Prepare update values
                update_values = [
                    (int(row[key]) if row[key] is not None else '') for key in [
                        'Provision Alpha Pack', 'Provision Beta Pack', 'Provision Gamma Pack',
                        'Basic Rare Pack 1', 'Basic Rare Pack 2',
                        'Basic Legend Alpha Pack 1', 'Basic Legend Alpha Pack 2',
                        'Advanced Epic Pack 1', 'Advanced Epic Pack 2'
                    ]
                ]

                update = {
                    'range': f'X{row_number}:AF{row_number}',
                    'values': [update_values]
                }
                print(f"Preparing update for row {row_number}: {update}")  # Debugging: print each prepared update
                updates.append(update)

        # Apply batch updates
        if updates:
            write_to_sheet(worksheet, updates)

        success_message = "Data written to sheet successfully"
        print(success_message)
        return success_message, 200

    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        return jsonify({'error': error_message}), 500