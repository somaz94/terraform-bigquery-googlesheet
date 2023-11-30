import os
import gspread
from google.oauth2.service_account import Credentials
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric
from datetime import datetime, timedelta

# Setup the Sheets and GA4 Data API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/analytics']
SERVICE_ACCOUNT_FILE = 'bigquery.json'  # Update this with the path to your service account file

# Load credentials
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Initialize the Sheets API client
gc = gspread.authorize(creds)

# The ID of the spreadsheet and GA4 property
SHEET_ID = os.getenv('SHEET_ID')  # Make sure this is set in your environment variables
GA_PROPERTY_ID = os.getenv('GA_PROPERTY_ID')  # Make sure this is set in your environment variables

# Initialize the GA4 Data API client
analytics_client = BetaAnalyticsDataClient(credentials=creds)

def get_ga4_data(property_id):
    """Fetches the number of new users from GA4 Data API."""
    try:
        request = RunReportRequest(
            property=f'properties/{property_id}',
            date_ranges=[DateRange(start_date='yesterday', end_date='yesterday')],
            metrics=[Metric(name='newUsers')]
        )
        response = analytics_client.run_report(request)
        return response.rows[0].metric_values[0].value
    except Exception as e:
        print(f"Error fetching GA4 data: {e}")
        return None

def update_sheet(gc, sheet_id, date_str, data):
    """Updates the specified Google Sheet with new data."""
    if data is None:
        print("No data to update.")
        return

    worksheet = gc.open_by_key(sheet_id).worksheet('Somaz_Community')

    # Find the cell with yesterday's date or append it if not found
    try:
        cell = worksheet.find(date_str)
    except gspread.exceptions.CellNotFound:
        next_row = len(worksheet.col_values(1)) + 1
        worksheet.update_cell(next_row, 1, date_str)
        cell = gspread.models.Cell(next_row, 1, value=date_str)

    # Update the cell with new data and center-align it
    worksheet.update_cell(cell.row, 8, data)
    # Set the format for the cell
    worksheet.format(f'H{cell.row}', {
        "horizontalAlignment": "CENTER"
    })

def update_analytics_data_in_sheets(request):
    """Cloud Function to be triggered by HTTP request to update GA data in Sheets."""
    new_users = get_ga4_data(GA_PROPERTY_ID)
    kst = datetime.utcnow() + timedelta(hours=9)  # Convert UTC to KST
    yesterday_kst = (kst - timedelta(days=1)).strftime('%Y-%m-%d')
    update_sheet(gc, SHEET_ID, yesterday_kst, new_users)
    return f'Updated sheet with {new_users} new users for {yesterday_kst}'

if __name__ == '__main__':
    # For local testing, you can trigger the function with a mock request
    class MockRequest:
        def get_json(self):
            return {}

    update_analytics_data_in_sheets(MockRequest())

