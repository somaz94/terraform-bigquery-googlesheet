import os
import gspread
import re
from datetime import datetime, timedelta
from google.oauth2 import service_account

# Setup the Sheets and GA4 Data API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/analytics']
SERVICE_ACCOUNT_FILE = 'bigquery.json'

# Load credentials
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Initialize the Sheets API client
gc = gspread.authorize(creds)

def copy_formulas_for_date(sheet, column_letter, date_row, prev_date_row):
    """Copy formulas from previous date row to the given date row for a specific column."""
    try:
        original_formula = sheet.acell(f'{column_letter}{prev_date_row}', value_render_option='FORMULA').value
        print(f"Original formula in {column_letter}{prev_date_row}: {original_formula}")  # Debug print

        if not isinstance(original_formula, str):
            print(f"Formula not found or not a string in cell {column_letter}{prev_date_row}: {original_formula}")
            return

        # Regex to find all cell references in the formula
        cell_references = re.findall(r'([A-Z]+)(\d+)', original_formula)
        if cell_references:
            updated_formula = original_formula
            for col_ref, row_ref in cell_references:
                new_row_number = int(row_ref) + 1  # Incrementing the row number
                updated_formula = re.sub(rf'{col_ref}{row_ref}', f'{col_ref}{new_row_number}', updated_formula)

            # Update the cell with the new formula
            sheet.update_acell(f'{column_letter}{date_row}', updated_formula)
        else:
            print(f"No cell references found in formula: {original_formula}")

    except Exception as e:
        print(f"Error processing cell {column_letter}{prev_date_row}: {e}")


def propagate_formulas(request):
    # IDs and Sheet names
    sheet_id = os.getenv('SHEET_ID')  # Get the sheet ID from environment variables
    community_sheet_name = 'KPI_Community'
    table_sheet_name = 'KPI_Table'

    # Open the worksheets
    community_sheet = gc.open_by_key(sheet_id).worksheet(community_sheet_name)
    table_sheet = gc.open_by_key(sheet_id).worksheet(table_sheet_name)

    # Calculate the dates
    today = datetime.utcnow().date()
    one_day_before = today - timedelta(days=1)
    two_days_before = today - timedelta(days=2)

    # Convert dates to string in the format that matches your sheet
    one_day_before_str = one_day_before.strftime('%Y-%m-%d')
    two_days_before_str = two_days_before.strftime('%Y-%m-%d')

    # Find the rows for the respective dates
    try:
        # For KPI_Community sheet
        one_day_before_row_community = community_sheet.find(one_day_before_str, in_column=1).row
        two_days_before_row_community = community_sheet.find(two_days_before_str, in_column=1).row
        
        # For KPI_Table sheet
        one_day_before_row_table = table_sheet.find(one_day_before_str, in_column=1).row
        two_days_before_row_table = table_sheet.find(two_days_before_str, in_column=1).row

    except gspread.exceptions.CellNotFound:
        # Handle the case where the dates are not found
        print(f"Date not found in the sheet")
        return

    # Update the KPI_Community sheet
    community_columns = ['I', 'M']
    for col in community_columns:
        copy_formulas_for_date(community_sheet, col, one_day_before_row_community, two_days_before_row_community)

    # Update the KPI_Table sheet
    table_columns = ['C', 'E', 'F', 'H', 'K', 'DM', 'DN'] + \
                    ['BG', 'BH', 'BI', 'BJ', 'BK', 'CK', 'CL', 'CM', 'CN', 'CO', 'CZ', 'DA', 'DB', 'DC', 'DD', 'DE', 'DF', 'DG']  # Added new columns here
    for col in table_columns:
        copy_formulas_for_date(table_sheet, col, one_day_before_row_table, two_days_before_row_table)

    return f"Formulas propagated to rows for {one_day_before_str} in both sheets."

# The function can be tested locally by passing a mock request
if __name__ == '__main__':
    class MockRequest:
        def get_json(self):
            return {}

    propagate_formulas(MockRequest())


