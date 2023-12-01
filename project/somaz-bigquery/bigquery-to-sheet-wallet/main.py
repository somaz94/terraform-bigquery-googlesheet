import os
import gspread
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
import logging
from datetime import datetime, timedelta
import pandas as pd

# Configure logging at the start of the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_wallet_datas_in_sheets(request):
    try:
        # Setup and connect to BigQuery and Google Sheets
        client = bigquery.Client()
        creds = Credentials.from_service_account_file('bigquery-luxon.json', scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ])
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(os.getenv('SHEET_ID'))
        worksheet = sh.worksheet('Somaz_Community')
        
        # Determine the date to query for
        today = datetime.now()
        if today.day == 1:
            # If it's the first day of the month, get the last day of the previous month
            date_to_query = get_last_day_of_previous_month()
        else:
            # Otherwise, just get yesterday's date
            date_to_query = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Execute query once and store results
        query_results = complex_query_1(client)
        query_results['date'] = pd.to_datetime(query_results['date']).dt.strftime('%Y-%m-%d')

        # Update sheets with query results for the determined date
        execute_and_update_for_query(client, worksheet, date_to_query, query_results, get_complex_query_1_mapping())

        return "Data updated successfully", 200
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

def execute_and_update_for_query(client, worksheet, date, query, column_mapping):
    results = query
    for item_name, column in column_mapping.items():
        update_sheet_for_item(worksheet, results, item_name, column, date)

def get_last_day_of_previous_month():
    first_day_of_current_month = datetime.now().replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    return last_day_of_previous_month.strftime("%Y-%m-%d")

def update_sheet_for_item(worksheet, results, item_name, column, date):
    try:
        date_cell = find_date_cell(worksheet, date)
        if date_cell:
            cell = f'{column}{date_cell.row}'
            date_data = int(results[results['date'] == date][item_name].fillna(0).iloc[0])
            
            # Log the update
            logging.info(f"Updating {cell} with {date_data} for {item_name}")
            
            worksheet.update_acell(cell, date_data)
            worksheet.format(cell, {"horizontalAlignment": "CENTER"})
    except Exception as e:
        logging.error(f"Error updating sheet for {item_name} on {date}: {e}")

def find_date_cell(worksheet, date):
    try:
        return worksheet.find(date)
    except gspread.exceptions.CellNotFound:
        return None

def complex_query_1(client):
    complex_query_1 = """
    SELECT
        DATE(grouped_date) AS date,
        meta_count,
        face_count,
        quantity
    FROM 
        EXTERNAL_QUERY("somaz-bigquery.asia-northeast1.prod-somaz-db-connection", 
        '''
        SELECT 
            DATE(created_at) AS grouped_date,
            SUM(CASE WHEN wallet = 'meta' THEN 1 ELSE 0 END) AS meta_count,
            SUM(CASE WHEN wallet = 'face' THEN 1 ELSE 0 END) AS face_count,
            SUM(CASE WHEN wallet IN ('meta', 'face') THEN 1 ELSE 0 END) AS quantity
        FROM 
            user
        WHERE
            (YEAR(created_at) = YEAR(CURRENT_DATE()) AND MONTH(created_at) = MONTH(CURRENT_DATE()))
            OR (YEAR(created_at) = YEAR(CURRENT_DATE() - INTERVAL 1 MONTH) AND MONTH(created_at) = MONTH(CURRENT_DATE() - INTERVAL 1 MONTH))
        GROUP BY 
            DATE(created_at)
        '''
        )
    ORDER BY
        date;
    """
    return client.query(complex_query_1).result().to_dataframe()

def get_complex_query_1_mapping():
    return {
        "meta_count": "J",
        "face_count": "K",
        "quantity": "L"
        # ... Add mappings for other items ...
    }

if __name__ == "__main__":
    update_wallet_datas_in_sheets(None)
