import os
import gspread
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
import logging
from datetime import datetime, timedelta
import pandas as pd

# Configure logging to display the date, time, and log level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_kpi_table_pack(request):
    try:
        # Setup BigQuery and Google Sheets clients
        client = bigquery.Client()
        creds = Credentials.from_service_account_file(
            'bigquery.json',
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(os.getenv('SHEET_ID'))
        worksheet = sh.worksheet('Somaz_Table(Pack)')
        
        # Fetch badge and tier counts from BigQuery
        badge_counts = fetch_badge_counts(client)
        tier_counts = fetch_tier_counts(client)
        
        # Write the counts to the Google Sheet
        update_sheet_with_counts(worksheet, badge_counts, tier_counts)

        logging.info("Data updated successfully")
        return "Data updated successfully", 200
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

def fetch_badge_counts(client):
    # Query to fetch the count of badges from BigQuery
    badge_query = """
    SELECT badge_name, COUNT(*) as user_count
    FROM (
        SELECT 
            CASE
                WHEN badge = 2 THEN 'TITANIUM'
                WHEN badge = 1 THEN 'RED'
            END AS badge_name
        FROM 
            EXTERNAL_QUERY("somaz-bigquery.asia-northeast1.somaz-rank-db-connection", "SELECT badge FROM user_rank WHERE badge IN (1, 2);")
    ) AS subquery
    WHERE badge_name IS NOT NULL
    GROUP BY badge_name
    ORDER BY badge_name DESC;
    """
    job = client.query(badge_query)
    result = job.result().to_dataframe()
    return result.set_index('badge_name')['user_count'].to_dict()

def fetch_tier_counts(client):
    # Query to fetch the count of tiers from BigQuery
    tier_query = """
    SELECT tier_name, COUNT(*) as user_count
    FROM (
        SELECT 
            CASE tier
                WHEN 5 THEN 'PLATINUM'
                WHEN 4 THEN 'GOLD'
                WHEN 3 THEN 'SILVER'
                WHEN 2 THEN 'BRONZE'
                WHEN 1 THEN 'IRON'
            END AS tier_name
        FROM 
            EXTERNAL_QUERY("somaz-bigquery.asia-northeast1.somaz-rank-db-connection", "SELECT tier FROM user_rank WHERE tier != 0;")
    ) AS subquery
    WHERE tier_name IS NOT NULL
    GROUP BY tier_name
    ORDER BY tier_name DESC;
    """
    job = client.query(tier_query)
    result = job.result().to_dataframe()
    return result.set_index('tier_name')['user_count'].to_dict()

def next_available_row(lst):
    """Returns the index of the first empty cell in a column"""
    return len([i for i in lst if i]) + 1

def find_row_by_date(worksheet, date):
    """Find the row number for the given date in the first column."""
    col_values = worksheet.col_values(1)
    for idx, val in enumerate(col_values):
        
        # Cleaning the value and comparing
        val_cleaned = val.strip()
        if val_cleaned == date:
            return idx + 1  # Found the row
    return None  # Date not found


def update_sheet_with_counts(worksheet, badge_counts, tier_counts):
    # Set the current date as the first date of the month
    first_day_of_month = datetime.now().replace(day=1).strftime("%Y-%m-%d")

    # Find the row for the first day of the month
    row_to_update = find_row_by_date(worksheet, first_day_of_month)
    if row_to_update is None:
        logging.error(f"The first day of the month {first_day_of_month} is not found in the sheet")
        return

    # Write the date in the first column (usually a column representing the date)
    # The next available row is not needed since we're updating an existing row
    worksheet.update_acell(f'A{row_to_update}', first_day_of_month)

    # Prepare the data to write to the sheet
    # Mapping the tier/badge names to the corresponding column letters in the sheet
    tier_mapping = {
        'PLATINUM': 'C',
        'GOLD': 'D',
        'SILVER': 'E',
        'BRONZE': 'F',
        'IRON': 'G',
    }
    badge_mapping = {
        'RED': 'H',
        'TITANIUM': 'I',
    }

    # Write tier counts
    for tier_name, column in tier_mapping.items():
        cell = f'{column}{row_to_update}'
        value = tier_counts.get(tier_name, 0)
        worksheet.update_acell(cell, value)

    # Write badge counts
    for badge_name, column in badge_mapping.items():
        cell = f'{column}{row_to_update}'
        value = badge_counts.get(badge_name, 0)
        worksheet.update_acell(cell, value)

if __name__ == "__main__":
    # This allows the script to be run directly
    update_kpi_table_pack(None)
