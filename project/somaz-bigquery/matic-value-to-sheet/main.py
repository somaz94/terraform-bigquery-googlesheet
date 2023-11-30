import os
import gspread
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime, timedelta

# Google Sheets scope and credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'bigquery.json'

# Load credentials
creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Connect to Google Sheets
gc = gspread.authorize(creds)

# The ID of the spreadsheet to update.
SHEET_ID = os.getenv('SHEET_ID')

# Function to get data from CoinGecko API
def get_polygon_data():
    # Get the current UTC date
    today = datetime.utcnow().date()
    start_of_today_utc = datetime.combine(today, datetime.min.time())
    
    # Convert to UNIX timestamps
    start_timestamp = int(start_of_today_utc.timestamp())
    end_timestamp = start_timestamp + 86400  # Add one day's worth of seconds
    
    # API request for today's price data
    # https://apiguide.coingecko.com/getting-started/endpoint-overview
    # https://www.coingecko.com/api/documentation
    url = 'https://api.coingecko.com/api/v3/coins/matic-network/market_chart/range'
    params = {
        'vs_currency': 'usd',
        'from': start_timestamp,
        'to': end_timestamp
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # Retrieve the first price point, which should be the opening price
    prices = data.get('prices', [])
    if prices:
        # Assuming the first price of the day (00:00 UTC) is the opening price
        # and taking into account the API's granularity and caching mechanism as described
        # The opening price is the first price in the list
        opening_price = prices[0][1]  # The price is the second item in the list
        return round(opening_price, 6)
    else:
        # Handle the case where no price data is available
        return None

def update_sheet(gc, sheet_id, today, opening_price):
    # Open the spreadsheet and the specific sheet
    sh = gc.open_by_key(sheet_id)
    worksheet = sh.worksheet('Somaz_Table')  # Make sure the sheet name is correct

    # Try to find the cell with today's date
    try:
        cell = worksheet.find(today)
        row_number = cell.row
    except gspread.exceptions.CellNotFound:
        # If today's date is not found, find the next empty row at the bottom of the sheet
        all_values = worksheet.get_all_values()
        row_number = len(all_values) + 1 if all_values else 1

    # Update the cell in column CY with new data
    cy_column = 'CY'  # Adjust the column as needed
    cell_range = f'{cy_column}{row_number}'
    worksheet.update(cell_range, [[opening_price]], value_input_option='USER_ENTERED')  # Ensure data is a list of lists

    # Apply formatting for center alignment and two decimal places
    worksheet.format(cell_range, {
        "horizontalAlignment": "CENTER",
        "numberFormat": {"type": "NUMBER", "pattern": "#,##0.00"}
    })

    print(f'{cell_range} updated.')

def update_polygon_data_in_sheets(request):
    opening_price = get_polygon_data()
    today = datetime.utcnow().strftime('%Y-%m-%d')  # Get today's date as a string

    if opening_price is not None:
        # Update the sheet with the opening price
        update_sheet(gc, SHEET_ID, today, opening_price)
    else:
        # Log an error or handle the case where no data was retrieved
        print("No opening price data available.")

    return 'Updated the sheet with new data'

if __name__ == "__main__":
    update_polygon_data_in_sheets(None)  # Example call

