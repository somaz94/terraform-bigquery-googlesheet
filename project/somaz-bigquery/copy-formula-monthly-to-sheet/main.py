import os
import gspread
import re
import time
from datetime import datetime, timedelta
from google.oauth2 import service_account
from gspread.exceptions import CellNotFound
from gspread.utils import a1_to_rowcol
from gspread import Cell
from googleapiclient.errors import HttpError as APIError

# Setup the Sheets and GA4 Data API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/analytics']
SERVICE_ACCOUNT_FILE = 'bigquery.json'

# Load credentials
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Initialize the Sheets API client
gc = gspread.authorize(creds)

def get_all_dates(sheet):
    """Fetch all dates from the first column of the sheet."""
    time.sleep(0.5)  # Delay before reading
    return exponential_backoff_retry(lambda: sheet.col_values(1))

def process_columns(sheet, specific_columns, date_row_mappings, updated_cells):
    """Process given columns to update formulas."""
    for col in specific_columns:
        prev_date_row = date_row_mappings.get('prev_date_row')
        date_row = date_row_mappings.get('date_row')
        if prev_date_row and date_row:
            copy_formulas_for_date(sheet, col, date_row, prev_date_row, updated_cells)

def is_first_day_of_month(date):
    """Check if the given date is the first day of its month."""
    return date.day == 1

def get_row_for_date(all_dates, date_str):
    """Retrieve the row number for a specific date string."""
    # Debug: Print the date string being searched for
    print(f"Searching for date: {date_str}")

    try:
        # Debug: Print a sample of dates from the sheet for comparison
        print(f"Sample dates from sheet: {all_dates[:10]}")

        # Using strip to remove any leading/trailing whitespace
        all_dates = [d.strip() for d in all_dates]
        return all_dates.index(date_str) + 1  # Add 1 because list index is 0-based and sheet rows are 1-based
    except ValueError:
        print(f"Date '{date_str}' not found in the sheet.")
        return None

def exponential_backoff_retry(func, max_attempts=5, initial_wait=1.0, backoff_factor=2.0):
    attempts = 0
    wait_time = initial_wait
    while attempts < max_attempts:
        try:
            return func()
        except APIError as e:
            if e.response.status_code == 429:  # Quota exceeded
                print(f"Quota exceeded, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= backoff_factor
                attempts += 1
            else:
                raise  # Reraise for non-quota errors
    raise Exception("Maximum retry attempts exceeded")

def wait_until_next_minute():
    """Wait until the start of the next minute."""
    now = datetime.now()
    wait_time = 61 - now.second
    print(f"Waiting for {wait_time} seconds until the start of the next minute...")
    time.sleep(wait_time)

def update_cells_in_chunks(sheet, cells, chunk_size=10):
    for i in range(0, len(cells), chunk_size):
        chunk = cells[i:i + chunk_size]
        exponential_backoff_retry(lambda: sheet.update_cells(chunk, value_input_option='USER_ENTERED'))
        print(f"Updated chunk of {chunk_size} cells, waiting before next batch...")
        time.sleep(2)  # Increased delay to 2 seconds between batches


def copy_formulas_for_date(sheet, column_letter, date_row, prev_date_row, updated_cells):
    """Prepare formulas from previous date row to be updated in the given date row for a specific column."""
    time.sleep(0.5)  # Delay before reading
    try:
        original_formula = sheet.acell(f'{column_letter}{prev_date_row}', value_render_option='FORMULA').value
        if not isinstance(original_formula, str):
            return
        
        print(f"Updating formula in column {column_letter}, row {date_row} based on row {prev_date_row}")  # Debug print

        cell_references = re.findall(r'([A-Z]+)(\d+)', original_formula)
        if cell_references:
            updated_formula = original_formula
            for col_ref, row_ref in cell_references:
                new_row_number = int(row_ref) + (date_row - prev_date_row)
                updated_formula = re.sub(rf'{col_ref}{row_ref}', f'{col_ref}{new_row_number}', updated_formula)
            column_index = a1_to_rowcol(column_letter + '1')[1]
            updated_cells.append(Cell(row=date_row, col=column_index, value=updated_formula))
    except Exception as e:
        print(f"Error processing cell {column_letter}{prev_date_row}: {e}")

def process_columns_in_order(sheet, columns, date_row_mappings, updated_cells):
    """Process columns in the specified order to update formulas."""
    for col in columns:
        print(f"Processing column {col}")
        prev_date_row = date_row_mappings.get('prev_date_row')
        date_row = date_row_mappings.get('date_row')
        if prev_date_row and date_row:
            copy_formulas_for_date(sheet, col, date_row, prev_date_row, updated_cells)

def propagate_formulas(request):
    sheet_id = os.getenv('SHEET_ID')  # Get the sheet ID from environment variables
    table_sheet_name = 'KPI_Table(Pack)'

    table_sheet = gc.open_by_key(sheet_id).worksheet(table_sheet_name)

    today = datetime.utcnow().date()
    first_day_of_previous_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_of_two_months_ago = first_day_of_previous_month - timedelta(days=1)
    first_day_of_two_months_ago = last_day_of_two_months_ago.replace(day=1)

    # Format these dates
    first_day_of_previous_month_str = first_day_of_previous_month.strftime('%Y-%m-%d')
    first_day_of_two_months_ago_str = first_day_of_two_months_ago.strftime('%Y-%m-%d')
    last_day_of_two_months_ago_str = last_day_of_two_months_ago.strftime('%Y-%m-%d')

    print(f"Searching for first day of previous month: {first_day_of_previous_month_str}")
    print(f"Searching for first day of two months ago: {first_day_of_two_months_ago_str}")
    print(f"Searching for last day of two months ago: {last_day_of_two_months_ago_str}")

    specific_columns = ['J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U' , 'V', 'W']
    other_columns = ['AG', 'AH', 'AI', 'AJ', 'AK', 'AX', 'AY', 'AZ', 'BA', 'BB']

    # Fetch all dates in the first column once
    all_dates = get_all_dates(table_sheet)

    first_day_of_previous_month_row = get_row_for_date(all_dates, first_day_of_previous_month_str)
    first_day_of_two_months_ago_row = get_row_for_date(all_dates, first_day_of_two_months_ago_str)
    last_day_of_two_months_ago_row = get_row_for_date(all_dates, last_day_of_two_months_ago_str)

    updated_cells = []

    # Check if rows are found
    if not first_day_of_previous_month_row or not first_day_of_two_months_ago_row:
        return "Required dates not found in the sheet"

    print(f"Updating specific columns: {specific_columns}")
    for col in specific_columns:
        print(f"Processing column {col}")
        copy_formulas_for_date(table_sheet, col, first_day_of_previous_month_row, first_day_of_two_months_ago_row, updated_cells)

    # Get row numbers for required dates
    date_row_mappings = {
        'date_row': get_row_for_date(all_dates, first_day_of_previous_month_str),
        'prev_date_row': get_row_for_date(all_dates, first_day_of_two_months_ago_str)
    }

    # Process specific_columns and other_columns in order
    process_columns_in_order(table_sheet, specific_columns, date_row_mappings, updated_cells)
    process_columns_in_order(table_sheet, other_columns, date_row_mappings, updated_cells)


    # Temporarily skip processing other_columns to debug
    skip_other_columns = False  # Set this to False to enable processing of other_columns

    if not skip_other_columns:
        for col in other_columns:
            print(f"Processing column {col}")  # 디버깅을 위한 출력
            for day in range(first_day_of_two_months_ago_row, last_day_of_two_months_ago_row + 1):
                target_row = day + (first_day_of_previous_month_row - first_day_of_two_months_ago_row)
                if day < last_day_of_two_months_ago_row:  # 이번달 1일은 제외
                    print(f"Updating column {col} for day {day} at target row {target_row}")  # 디버깅을 위한 출력
                    copy_formulas_for_date(table_sheet, col, target_row, day, updated_cells)

    # Batch update to optimize API calls
    if updated_cells:
        try:
            # Wrapping the update call in the retry logic
            update_cells_in_chunks(table_sheet, updated_cells, chunk_size=10)  # You can adjust the chunk size
            print("Batch update successful")
        except Exception as e:
            print(f"Batch update failed: {e}")

    return f"Formulas propagated to rows for {first_day_of_previous_month_str} in both sheets."

if __name__ == '__main__':
    response = propagate_formulas(None)  # No actual request object needed for local testing
    print(response)
