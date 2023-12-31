import os
import requests
import datetime
import calendar
import gspread
from google.oauth2.service_account import Credentials
from flask import jsonify
import time

def fetch_data_from_dune():
    API_KEY = os.getenv('DUNE_API_KEY')
    PREMIUM_QUERY_ID = '' # Replace with your actual query ID

    headers = {
        "Content-Type": "application/json",
        "X-Dune-API-Key": API_KEY
    }

    def execute_query(query_id):
        payload = {"parameters": []}
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

    return execute_query(PREMIUM_QUERY_ID)

def aggregate_data(data):
    today = datetime.date.today()
    previous_month = today.replace(day=1) - datetime.timedelta(days=1)
    days_in_month = calendar.monthrange(previous_month.year, previous_month.month)[1]

    # Set the cutoff based on the number of days in the month
    first_half_cutoff = 14 if days_in_month == 30 else 15
    second_half_start = 15 if days_in_month == 30 else 16

    first_half_agg = 0
    second_half_agg = 0

    for row in data:
        date_key = row['일자(KST)' if '일자(KST)' in row else '일자']
        try:
            date_obj = datetime.datetime.strptime(date_key, '%Y-%m-%d').date()
            quest_completion_count = int(row.get('퀘스트 완료 수', 0))  # Ensure it's an integer
            if date_obj.year == previous_month.year and date_obj.month == previous_month.month:
                if date_obj.day <= first_half_cutoff:
                    first_half_agg += quest_completion_count
                elif date_obj.day >= second_half_start:
                    second_half_agg += quest_completion_count
        except ValueError as e:
            print(f"Error parsing date or quest completion count: {e}, row: {row}")

    print(f"First half aggregate: {first_half_agg}, Second half aggregate: {second_half_agg}")
    return first_half_agg, second_half_agg

def find_row_for_month_and_range(worksheet, month_str, date_range):
    try:
        month_column_values = worksheet.col_values(1)
        date_range_column_values = worksheet.col_values(2)
        for i, (month, date_range_cell) in enumerate(zip(month_column_values, date_range_column_values)):
            if month.strip().lower() == month_str.strip().lower() and date_range_cell.strip() == date_range.strip():
                return i + 1  # Adjusting for zero-indexing
        return None
    except Exception as e:
        print(f"Error in find_row_for_month_and_range: {e}")
        return None

def write_to_sheet(worksheet, row_number, data):
    if row_number is None or row_number < 2:
        print("Invalid row number in the sheet")
        return

    columns = {
        'Y': data
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
        global_data = fetch_data_from_dune()
        if not global_data:
            error_message = "Failed to fetch data from Dune Analytics."
            print(error_message)
            return jsonify({'error': error_message})

        # 이전 달의 날짜를 'YYYY-MM' 형식으로 구하기
        previous_month = datetime.datetime.now().replace(day=1) - datetime.timedelta(days=1)
        previous_month_str = previous_month.strftime('%Y-%m')

        # 집계 데이터 계산
        first_half_agg, second_half_agg = aggregate_data(global_data)

        # Google Sheets 접근 설정
        creds = Credentials.from_service_account_file('bigquery.json', scopes=['https://www.googleapis.com/auth/spreadsheets'])
        gc = gspread.authorize(creds)
        SHEET_ID = os.getenv('SHEET_ID')
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.worksheet("[Quest]Premium")

        # 이전 달의 일수에 따른 범위 설정
        days_in_month = calendar.monthrange(previous_month.year, previous_month.month)[1]

        # 첫 번째 날짜 범위 설정
        first_range = "1~ 14일" if previous_month.month == 2 or days_in_month == 30 else "1~ 15일"
        
        # 두 번째 날짜 범위 설정
        if previous_month.month == 2:  # 2월인 경우
            second_range = "15~29일" if calendar.isleap(previous_month.year) else "15~28일"
        else:
            second_range = "15~30일" if days_in_month == 30 else "16~31일"

        # 해당 월과 범위에 대한 행 번호 찾기
        first_row_number = find_row_for_month_and_range(worksheet, previous_month_str, first_range)
        second_row_number = find_row_for_month_and_range(worksheet, previous_month_str, second_range)

        # 시트에 데이터 작성
        if first_row_number:
            write_to_sheet(worksheet, first_row_number, first_half_agg)
        if second_row_number:
            write_to_sheet(worksheet, second_row_number, second_half_agg)

        print("Data written to sheet successfully")
        return "Data written to sheet successfully", 200

    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        return jsonify({'error': error_message}), 500
    
    

