import os
import gspread
import time
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric

# Setup the Sheets and GA4 Data API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/analytics']
SERVICE_ACCOUNT_FILE = 'bigquery.json'

# Load credentials
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Initialize the GA4 Data API client
analytics_client = BetaAnalyticsDataClient(credentials=creds)

# Initialize the Sheets API client
gc = gspread.authorize(creds)

# IDs and Sheet name
SHEET_ID = os.getenv('SHEET_ID')  # From environment variable
GA_PROPERTY_ID = os.getenv('GA_PROPERTY_ID')  # From environment variable
SHEET_NAME = 'KPI_Somaz Web'

# Function to run the report on GA4 Data API
def run_report(client, property_id, start_date, end_date):
    request = RunReportRequest(
        property=f'properties/{property_id}',
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[{'name': 'country'}],  # Ensure 'country' is a valid dimension for your GA property.
        metrics=[{'name': 'newUsers'}]
    )
    response = client.run_report(request)
    return response

def col_num_to_letter(col_num):
    """Convert a column number (e.g., 28) to a column letter (e.g., AB)."""
    letter = ''
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        letter = chr(65 + remainder) + letter
    return letter

def update_sheet_with_data(gc, sheet_id, data_difference, sheet_name):
    """Updates the specified Google Sheet with the data difference by country."""
    worksheet = gc.open_by_key(sheet_id).worksheet(sheet_name)

    # Get current date (as of UTC)
    current_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')

    # Find a row that matches the date
    try:
        date_cell = worksheet.find(current_date, in_column=1)
        row = date_cell.row
    except gspread.exceptions.CellNotFound:
        # If there is no date, add a new row
        row = len(worksheet.col_values(1)) + 1
        worksheet.update_cell(row, 1, current_date)

    # Get all country names in one request
    countries_in_sheet = worksheet.batch_get(['D1:BP1'])[0][0]

    # Data and formatting updates grouped together
    data_updates = []
    format_updates = {
        "requests": []
    }

    for country, value in data_difference.items():
        if country in countries_in_sheet:
            col = countries_in_sheet.index(country) + 4  # Offset for column D start
            cell_addr = f'{col_num_to_letter(col)}{row}'
            data_updates.append({
                'range': cell_addr,
                'values': [[value]]
            })
            format_updates["requests"].append({
                "repeatCell": {
                    "range": {
                        "sheetId": worksheet.id,
                        "startRowIndex": row-1,
                        "endRowIndex": row,
                        "startColumnIndex": col-1,
                        "endColumnIndex": col
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER"
                        }
                    },
                    "fields": "userEnteredFormat(horizontalAlignment)"
                }
            })

            # Perform batch update every 10 countries and add delay
            if len(data_updates) >= 10:
                worksheet.batch_update(data_updates)
                worksheet.spreadsheet.batch_update(format_updates)
                data_updates = []
                format_updates = {
                    "requests": []
                }
                time.sleep(2)  # Delay to avoid hitting write quota

    # Perform batch update for any remaining data and formatting
    if data_updates:
        worksheet.batch_update(data_updates)
        worksheet.spreadsheet.batch_update(format_updates)

# Cloud Function entry point
def update_analytics_data_in_sheets(request):
    # Fetch data for the two periods
    start_date = '2022-10-26'
    end_date_first = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date_second = (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d')

    data_first_period = run_report(analytics_client, GA_PROPERTY_ID, start_date, end_date_first)
    data_second_period = run_report(analytics_client, GA_PROPERTY_ID, start_date, end_date_second)

    # Process the data and calculate the difference by country
    country_data_first = {}
    country_data_second = {}

    for row in data_first_period.rows:
        country_name = row.dimension_values[0].value
        new_users = int(row.metric_values[0].value)
        country_data_first[country_name] = new_users

    for row in data_second_period.rows:
        country_name = row.dimension_values[0].value
        new_users = int(row.metric_values[0].value)
        country_data_second[country_name] = new_users

    data_difference = {country: country_data_first.get(country, 0) - country_data_second.get(country, 0)
                       for country in country_data_first.keys()}

    # Update data to Google Sheet
    update_sheet_with_data(gc, SHEET_ID, data_difference, SHEET_NAME)

    print("Google Sheet updated with data difference by country.")

    return "Google Sheet updated successfully."

# The function can be tested locally by passing a mock request
if __name__ == '__main__':
    class MockRequest:
        def get_json(self):
            return {}

    update_analytics_data_in_sheets(MockRequest())


