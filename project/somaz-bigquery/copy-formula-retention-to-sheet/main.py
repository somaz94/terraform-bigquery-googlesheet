import os
import gspread
import re
import time
from datetime import datetime, timedelta
from google.oauth2 import service_account
from gspread.exceptions import APIError
from gspread.utils import a1_to_rowcol, rowcol_to_a1
from gspread import Cell

# Setup the Sheets and GA4 Data API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/analytics']
SERVICE_ACCOUNT_FILE = 'bigquery.json'

# Load credentials
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Initialize the Sheets API client
gc = gspread.authorize(creds)

def exponential_backoff_retry(func, max_attempts=5, initial_wait=1.0, backoff_factor=2.0):
    attempts = 0
    wait_time = initial_wait
    while attempts < max_attempts:
        try:
            return func()
        except APIError as e:
            if e.response.status_code == 429:
                print(f"Quota exceeded, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                attempts += 1
                wait_time *= backoff_factor
            else:
                raise e
    raise Exception("Maximum retry attempts exceeded")

def wait_until_next_minute():
    """Wait until the start of the next minute."""
    now = datetime.now()
    wait_time = 61 - now.second
    print(f"Waiting for {wait_time} seconds until the start of the next minute...")
    time.sleep(wait_time)

def update_cells_in_chunks(sheet, cells, chunk_size=10):
    """
    Update cells in chunks with a delay between each chunk to avoid hitting quotas.
    Apply center alignment to the updated cells.
    """
    for i in range(0, len(cells), chunk_size):
        chunk = cells[i:i + chunk_size]
        try:
            exponential_backoff_retry(lambda: sheet.update_cells(chunk, value_input_option='USER_ENTERED'))

            # Convert the first and last cell's row and column to A1 notation
            start_cell = rowcol_to_a1(chunk[0].row, chunk[0].col)
            end_cell = rowcol_to_a1(chunk[-1].row, chunk[-1].col)
            cell_range = f"{start_cell}:{end_cell}"

            # Apply center alignment to the updated cells
            sheet.format(cell_range, {"horizontalAlignment": "CENTER"})

        except APIError as e:
            if e.response.status_code == 429:  # Quota exceeded
                wait_until_next_minute()  # Wait until the start of the next minute
            else:
                raise e

def copy_formulas_for_date(sheet, column_letter, date_row, prev_date_row, updated_cells):
    """
    Copy formulas from the previous date row to the given date row for a specific column.
    """
    try:
        original_formula = exponential_backoff_retry(lambda: sheet.acell(f'{column_letter}{prev_date_row}', value_render_option='FORMULA').value)
        if not isinstance(original_formula, str):
            return

        # Replace row numbers in the formula to point to the new date row
        updated_formula = re.sub(r'([A-Z]+)(\d+)', lambda x: f"{x.group(1)}{int(x.group(2)) + (date_row - prev_date_row)}", original_formula)
        
        # Create a cell object with the updated formula
        col_number = a1_to_rowcol(column_letter + '1')[1]
        updated_cells.append(Cell(row=date_row, col=col_number, value=updated_formula))
    except Exception as e:
        print(f"Error processing cell {column_letter}{prev_date_row}: {e}")

def get_column_letter(col_num):
    """
    Converts a column number (e.g., 27) into a column letter (e.g., 'AA').
    """
    letter = ''
    while col_num > 0:
        col_num, remainder = divmod(col_num - 1, 26)
        letter = chr(65 + remainder) + letter
    return letter

def propagate_formulas(request):
    """
    Propagate formulas in the Somaz_Retention sheet for columns from C to Z.
    """
    sheet_id = os.getenv('SHEET_ID') 
    sheet_name = 'Somaz_Retention'

    # Open the worksheet
    sheet = gc.open_by_key(sheet_id).worksheet(sheet_name)

    # Calculate dates
    today = datetime.utcnow().date()
    two_days_before = today - timedelta(days=2)
    one_day_before = today - timedelta(days=1)

    two_days_before_str = two_days_before.strftime('%Y-%m-%d')
    one_day_before_str = one_day_before.strftime('%Y-%m-%d')

    # Find the rows for the respective dates
    all_dates = exponential_backoff_retry(lambda: sheet.col_values(1))
    try:
        two_days_before_row = all_dates.index(two_days_before_str) + 1
        one_day_before_row = all_dates.index(one_day_before_str) + 1
    except ValueError:
        print(f"Date not found in the sheet: {two_days_before_str} or {one_day_before_str}")
        return

    updated_cells = []  # Initialize the updated_cells list here.

    # Define the range of columns to process
    start_col = 'C'
    end_col = 'FO'
    start_col_num = a1_to_rowcol(start_col + '1')[1]
    end_col_num = a1_to_rowcol(end_col + '1')[1]

    # Loop through each column and copy formulas
    for col_num in range(start_col_num, end_col_num + 1):
        col_letter = get_column_letter(col_num)
        copy_formulas_for_date(sheet, col_letter, one_day_before_row, two_days_before_row, updated_cells)

    # Update the sheet with all the modified cells in chunks
    if updated_cells:
        update_cells_in_chunks(sheet, updated_cells)

    return f"Formulas propagated to row for {one_day_before_str}."

if __name__ == '__main__':
    response = propagate_formulas()
    print(response)
