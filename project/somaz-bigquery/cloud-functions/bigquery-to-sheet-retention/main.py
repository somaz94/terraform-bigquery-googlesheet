import os
import gspread
import time
import pandas as pd
import logging
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from gspread.exceptions import APIError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_retention_datas_in_sheets(request):
    try:
        # Setup and connect to BigQuery and Google Sheets
        client = bigquery.Client()
        creds = Credentials.from_service_account_file('bigquery-dsp.json', scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ])
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(os.getenv('SHEET_ID'))
        worksheet = sh.worksheet('Somaz_Retention')

        # Execute the complex query
        query_results = complex_query_1(client)

        # Filter for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)  # Changed from 30 to 60 days
        query_results['dt'] = pd.to_datetime(query_results['_ec__9d__bc__ec__9e__90_']).dt.strftime('%Y-%m-%d')
        query_results = query_results[query_results['dt'].between(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))]

        # Check if there are any results to update
        if query_results.empty:
            logging.info("No data to update for the last 30 days.")
            return "No data to update for the last 30 days.", 200

        # Replace NaN or infinite values
        query_results.fillna("", inplace=True)

        # Update sheets with query results
        update_sheet_with_complex_query_results(worksheet, query_results)

        return "Data updated successfully", 200
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}", 500

def complex_query_1(client):
    # Define and execute the new query
    complex_query_1 = """
    SELECT * 
    FROM EXTERNAL_QUERY(
        "somaz-bigquery.asia-northeast1.somaz-game-log-db-connection", 
        '''
        SELECT 
          dt as '일자',
          MAX(CASE WHEN dt_plus = 1 THEN user_cnt ELSE NULL END) as 'D+1',
          MAX(CASE WHEN dt_plus = 2 THEN user_cnt ELSE NULL END) as 'D+2',
          MAX(CASE WHEN dt_plus = 3 THEN user_cnt ELSE NULL END) as 'D+3',
          MAX(CASE WHEN dt_plus = 4 THEN user_cnt ELSE NULL END) as 'D+4',
          MAX(CASE WHEN dt_plus = 5 THEN user_cnt ELSE NULL END) as 'D+5',
          MAX(CASE WHEN dt_plus = 6 THEN user_cnt ELSE NULL END) as 'D+6',
          MAX(CASE WHEN dt_plus = 7 THEN user_cnt ELSE NULL END) as 'D+7',
          MAX(CASE WHEN dt_plus = 8 THEN user_cnt ELSE NULL END) as 'D+8',
          MAX(CASE WHEN dt_plus = 9 THEN user_cnt ELSE NULL END) as 'D+9',
          MAX(CASE WHEN dt_plus = 10 THEN user_cnt ELSE NULL END) as 'D+10',
          MAX(CASE WHEN dt_plus = 11 THEN user_cnt ELSE NULL END) as 'D+11',
          MAX(CASE WHEN dt_plus = 12 THEN user_cnt ELSE NULL END) as 'D+12',
          MAX(CASE WHEN dt_plus = 13 THEN user_cnt ELSE NULL END) as 'D+13',
          MAX(CASE WHEN dt_plus = 14 THEN user_cnt ELSE NULL END) as 'D+14',
          MAX(CASE WHEN dt_plus = 15 THEN user_cnt ELSE NULL END) as 'D+15',
          MAX(CASE WHEN dt_plus = 16 THEN user_cnt ELSE NULL END) as 'D+16',
          MAX(CASE WHEN dt_plus = 17 THEN user_cnt ELSE NULL END) as 'D+17',
          MAX(CASE WHEN dt_plus = 18 THEN user_cnt ELSE NULL END) as 'D+18',
          MAX(CASE WHEN dt_plus = 19 THEN user_cnt ELSE NULL END) as 'D+19',
          MAX(CASE WHEN dt_plus = 20 THEN user_cnt ELSE NULL END) as 'D+20',
          MAX(CASE WHEN dt_plus = 21 THEN user_cnt ELSE NULL END) as 'D+21',
          MAX(CASE WHEN dt_plus = 22 THEN user_cnt ELSE NULL END) as 'D+22',
          MAX(CASE WHEN dt_plus = 23 THEN user_cnt ELSE NULL END) as 'D+23',
          MAX(CASE WHEN dt_plus = 24 THEN user_cnt ELSE NULL END) as 'D+24',
          MAX(CASE WHEN dt_plus = 25 THEN user_cnt ELSE NULL END) as 'D+25',
          MAX(CASE WHEN dt_plus = 26 THEN user_cnt ELSE NULL END) as 'D+26',
          MAX(CASE WHEN dt_plus = 27 THEN user_cnt ELSE NULL END) as 'D+27', 
          MAX(CASE WHEN dt_plus = 28 THEN user_cnt ELSE NULL END) as 'D+28',
          MAX(CASE WHEN dt_plus = 29 THEN user_cnt ELSE NULL END) as 'D+29',
          MAX(CASE WHEN dt_plus = 30 THEN user_cnt ELSE NULL END) as 'D+30',
          MAX(CASE WHEN dt_plus = 31 THEN user_cnt ELSE NULL END) as 'D+31',
          MAX(CASE WHEN dt_plus = 32 THEN user_cnt ELSE NULL END) as 'D+32',
          MAX(CASE WHEN dt_plus = 33 THEN user_cnt ELSE NULL END) as 'D+33',
          MAX(CASE WHEN dt_plus = 34 THEN user_cnt ELSE NULL END) as 'D+34',
          MAX(CASE WHEN dt_plus = 35 THEN user_cnt ELSE NULL END) as 'D+35',
          MAX(CASE WHEN dt_plus = 36 THEN user_cnt ELSE NULL END) as 'D+36',
          MAX(CASE WHEN dt_plus = 37 THEN user_cnt ELSE NULL END) as 'D+37',
          MAX(CASE WHEN dt_plus = 38 THEN user_cnt ELSE NULL END) as 'D+38',
          MAX(CASE WHEN dt_plus = 39 THEN user_cnt ELSE NULL END) as 'D+39',      
          MAX(CASE WHEN dt_plus = 40 THEN user_cnt ELSE NULL END) as 'D+40',
          MAX(CASE WHEN dt_plus = 41 THEN user_cnt ELSE NULL END) as 'D+41',
          MAX(CASE WHEN dt_plus = 42 THEN user_cnt ELSE NULL END) as 'D+42',
          MAX(CASE WHEN dt_plus = 43 THEN user_cnt ELSE NULL END) as 'D+43',
          MAX(CASE WHEN dt_plus = 44 THEN user_cnt ELSE NULL END) as 'D+44',
          MAX(CASE WHEN dt_plus = 45 THEN user_cnt ELSE NULL END) as 'D+45',
          MAX(CASE WHEN dt_plus = 46 THEN user_cnt ELSE NULL END) as 'D+46',
          MAX(CASE WHEN dt_plus = 47 THEN user_cnt ELSE NULL END) as 'D+47',
          MAX(CASE WHEN dt_plus = 48 THEN user_cnt ELSE NULL END) as 'D+48',
          MAX(CASE WHEN dt_plus = 49 THEN user_cnt ELSE NULL END) as 'D+49',
          MAX(CASE WHEN dt_plus = 50 THEN user_cnt ELSE NULL END) as 'D+50',
          MAX(CASE WHEN dt_plus = 51 THEN user_cnt ELSE NULL END) as 'D+51',
          MAX(CASE WHEN dt_plus = 52 THEN user_cnt ELSE NULL END) as 'D+52',
          MAX(CASE WHEN dt_plus = 53 THEN user_cnt ELSE NULL END) as 'D+53',
          MAX(CASE WHEN dt_plus = 54 THEN user_cnt ELSE NULL END) as 'D+54',
          MAX(CASE WHEN dt_plus = 55 THEN user_cnt ELSE NULL END) as 'D+55',
          MAX(CASE WHEN dt_plus = 56 THEN user_cnt ELSE NULL END) as 'D+56',
          MAX(CASE WHEN dt_plus = 57 THEN user_cnt ELSE NULL END) as 'D+57',
          MAX(CASE WHEN dt_plus = 58 THEN user_cnt ELSE NULL END) as 'D+58',
          MAX(CASE WHEN dt_plus = 59 THEN user_cnt ELSE NULL END) as 'D+59',
          MAX(CASE WHEN dt_plus = 60 THEN user_cnt ELSE NULL END) as 'D+60',
          MAX(CASE WHEN dt_plus = 61 THEN user_cnt ELSE NULL END) as 'D+61',
          MAX(CASE WHEN dt_plus = 62 THEN user_cnt ELSE NULL END) as 'D+62',
          MAX(CASE WHEN dt_plus = 63 THEN user_cnt ELSE NULL END) as 'D+63',
          MAX(CASE WHEN dt_plus = 64 THEN user_cnt ELSE NULL END) as 'D+64',
          MAX(CASE WHEN dt_plus = 65 THEN user_cnt ELSE NULL END) as 'D+65',
          MAX(CASE WHEN dt_plus = 66 THEN user_cnt ELSE NULL END) as 'D+66',
          MAX(CASE WHEN dt_plus = 67 THEN user_cnt ELSE NULL END) as 'D+67',
          MAX(CASE WHEN dt_plus = 68 THEN user_cnt ELSE NULL END) as 'D+68',
          MAX(CASE WHEN dt_plus = 69 THEN user_cnt ELSE NULL END) as 'D+69',
          MAX(CASE WHEN dt_plus = 70 THEN user_cnt ELSE NULL END) as 'D+70',
          MAX(CASE WHEN dt_plus = 71 THEN user_cnt ELSE NULL END) as 'D+71',
          MAX(CASE WHEN dt_plus = 72 THEN user_cnt ELSE NULL END) as 'D+72',
          MAX(CASE WHEN dt_plus = 73 THEN user_cnt ELSE NULL END) as 'D+73',
          MAX(CASE WHEN dt_plus = 74 THEN user_cnt ELSE NULL END) as 'D+74',
          MAX(CASE WHEN dt_plus = 75 THEN user_cnt ELSE NULL END) as 'D+75',
          MAX(CASE WHEN dt_plus = 76 THEN user_cnt ELSE NULL END) as 'D+76',
          MAX(CASE WHEN dt_plus = 77 THEN user_cnt ELSE NULL END) as 'D+77',
          MAX(CASE WHEN dt_plus = 78 THEN user_cnt ELSE NULL END) as 'D+78',
          MAX(CASE WHEN dt_plus = 79 THEN user_cnt ELSE NULL END) as 'D+79',
          MAX(CASE WHEN dt_plus = 80 THEN user_cnt ELSE NULL END) as 'D+80',
          MAX(CASE WHEN dt_plus = 81 THEN user_cnt ELSE NULL END) as 'D+81',
          MAX(CASE WHEN dt_plus = 82 THEN user_cnt ELSE NULL END) as 'D+82',
          MAX(CASE WHEN dt_plus = 83 THEN user_cnt ELSE NULL END) as 'D+83',
          MAX(CASE WHEN dt_plus = 84 THEN user_cnt ELSE NULL END) as 'D+84',
          MAX(CASE WHEN dt_plus = 85 THEN user_cnt ELSE NULL END) as 'D+85',
          MAX(CASE WHEN dt_plus = 86 THEN user_cnt ELSE NULL END) as 'D+86',
          MAX(CASE WHEN dt_plus = 87 THEN user_cnt ELSE NULL END) as 'D+87',
          MAX(CASE WHEN dt_plus = 88 THEN user_cnt ELSE NULL END) as 'D+88',
          MAX(CASE WHEN dt_plus = 89 THEN user_cnt ELSE NULL END) as 'D+89',
          MAX(CASE WHEN dt_plus = 90 THEN user_cnt ELSE NULL END) as 'D+90',
          MAX(CASE WHEN dt_plus = 91 THEN user_cnt ELSE NULL END) as 'D+91',
          MAX(CASE WHEN dt_plus = 92 THEN user_cnt ELSE NULL END) as 'D+92',
          MAX(CASE WHEN dt_plus = 93 THEN user_cnt ELSE NULL END) as 'D+93',
          MAX(CASE WHEN dt_plus = 94 THEN user_cnt ELSE NULL END) as 'D+94',
          MAX(CASE WHEN dt_plus = 95 THEN user_cnt ELSE NULL END) as 'D+95',
          MAX(CASE WHEN dt_plus = 96 THEN user_cnt ELSE NULL END) as 'D+96',
          MAX(CASE WHEN dt_plus = 97 THEN user_cnt ELSE NULL END) as 'D+97',
          MAX(CASE WHEN dt_plus = 98 THEN user_cnt ELSE NULL END) as 'D+98',
          MAX(CASE WHEN dt_plus = 99 THEN user_cnt ELSE NULL END) as 'D+99',
          MAX(CASE WHEN dt_plus = 100 THEN user_cnt ELSE NULL END) as 'D+100',
          MAX(CASE WHEN dt_plus = 101 THEN user_cnt ELSE NULL END) as 'D+101',
          MAX(CASE WHEN dt_plus = 102 THEN user_cnt ELSE NULL END) as 'D+102',
          MAX(CASE WHEN dt_plus = 103 THEN user_cnt ELSE NULL END) as 'D+103',
          MAX(CASE WHEN dt_plus = 104 THEN user_cnt ELSE NULL END) as 'D+104',
          MAX(CASE WHEN dt_plus = 105 THEN user_cnt ELSE NULL END) as 'D+105',
          MAX(CASE WHEN dt_plus = 106 THEN user_cnt ELSE NULL END) as 'D+106',
          MAX(CASE WHEN dt_plus = 107 THEN user_cnt ELSE NULL END) as 'D+107',
          MAX(CASE WHEN dt_plus = 108 THEN user_cnt ELSE NULL END) as 'D+108',
          MAX(CASE WHEN dt_plus = 109 THEN user_cnt ELSE NULL END) as 'D+109',
          MAX(CASE WHEN dt_plus = 110 THEN user_cnt ELSE NULL END) as 'D+110',
          MAX(CASE WHEN dt_plus = 111 THEN user_cnt ELSE NULL END) as 'D+111',
          MAX(CASE WHEN dt_plus = 112 THEN user_cnt ELSE NULL END) as 'D+112',
          MAX(CASE WHEN dt_plus = 113 THEN user_cnt ELSE NULL END) as 'D+113',
          MAX(CASE WHEN dt_plus = 114 THEN user_cnt ELSE NULL END) as 'D+114',
          MAX(CASE WHEN dt_plus = 115 THEN user_cnt ELSE NULL END) as 'D+115',
          MAX(CASE WHEN dt_plus = 116 THEN user_cnt ELSE NULL END) as 'D+116',
          MAX(CASE WHEN dt_plus = 117 THEN user_cnt ELSE NULL END) as 'D+117',
          MAX(CASE WHEN dt_plus = 118 THEN user_cnt ELSE NULL END) as 'D+118',
          MAX(CASE WHEN dt_plus = 119 THEN user_cnt ELSE NULL END) as 'D+119',
          MAX(CASE WHEN dt_plus = 120 THEN user_cnt ELSE NULL END) as 'D+120',
          MAX(CASE WHEN dt_plus = 121 THEN user_cnt ELSE NULL END) as 'D+121',
          MAX(CASE WHEN dt_plus = 122 THEN user_cnt ELSE NULL END) as 'D+122',
          MAX(CASE WHEN dt_plus = 123 THEN user_cnt ELSE NULL END) as 'D+123',
          MAX(CASE WHEN dt_plus = 124 THEN user_cnt ELSE NULL END) as 'D+124',
          MAX(CASE WHEN dt_plus = 125 THEN user_cnt ELSE NULL END) as 'D+125',
          MAX(CASE WHEN dt_plus = 126 THEN user_cnt ELSE NULL END) as 'D+126',
          MAX(CASE WHEN dt_plus = 127 THEN user_cnt ELSE NULL END) as 'D+127',
          MAX(CASE WHEN dt_plus = 128 THEN user_cnt ELSE NULL END) as 'D+128',
          MAX(CASE WHEN dt_plus = 129 THEN user_cnt ELSE NULL END) as 'D+129',
          MAX(CASE WHEN dt_plus = 130 THEN user_cnt ELSE NULL END) as 'D+130',
          MAX(CASE WHEN dt_plus = 131 THEN user_cnt ELSE NULL END) as 'D+131',
          MAX(CASE WHEN dt_plus = 132 THEN user_cnt ELSE NULL END) as 'D+132',
          MAX(CASE WHEN dt_plus = 133 THEN user_cnt ELSE NULL END) as 'D+133',
          MAX(CASE WHEN dt_plus = 134 THEN user_cnt ELSE NULL END) as 'D+134',
          MAX(CASE WHEN dt_plus = 135 THEN user_cnt ELSE NULL END) as 'D+135',
          MAX(CASE WHEN dt_plus = 136 THEN user_cnt ELSE NULL END) as 'D+136',
          MAX(CASE WHEN dt_plus = 137 THEN user_cnt ELSE NULL END) as 'D+137',
          MAX(CASE WHEN dt_plus = 138 THEN user_cnt ELSE NULL END) as 'D+138',
          MAX(CASE WHEN dt_plus = 139 THEN user_cnt ELSE NULL END) as 'D+139',
          MAX(CASE WHEN dt_plus = 140 THEN user_cnt ELSE NULL END) as 'D+140',
          MAX(CASE WHEN dt_plus = 141 THEN user_cnt ELSE NULL END) as 'D+141',
          MAX(CASE WHEN dt_plus = 142 THEN user_cnt ELSE NULL END) as 'D+142',
          MAX(CASE WHEN dt_plus = 143 THEN user_cnt ELSE NULL END) as 'D+143',
          MAX(CASE WHEN dt_plus = 144 THEN user_cnt ELSE NULL END) as 'D+144',
          MAX(CASE WHEN dt_plus = 145 THEN user_cnt ELSE NULL END) as 'D+145',
          MAX(CASE WHEN dt_plus = 146 THEN user_cnt ELSE NULL END) as 'D+146',
          MAX(CASE WHEN dt_plus = 147 THEN user_cnt ELSE NULL END) as 'D+147',
          MAX(CASE WHEN dt_plus = 148 THEN user_cnt ELSE NULL END) as 'D+148',
          MAX(CASE WHEN dt_plus = 149 THEN user_cnt ELSE NULL END) as 'D+149',
          MAX(CASE WHEN dt_plus = 150 THEN user_cnt ELSE NULL END) as 'D+150',
          MAX(CASE WHEN dt_plus = 151 THEN user_cnt ELSE NULL END) as 'D+151',
          MAX(CASE WHEN dt_plus = 152 THEN user_cnt ELSE NULL END) as 'D+152',
          MAX(CASE WHEN dt_plus = 153 THEN user_cnt ELSE NULL END) as 'D+153',
          MAX(CASE WHEN dt_plus = 154 THEN user_cnt ELSE NULL END) as 'D+154',
          MAX(CASE WHEN dt_plus = 155 THEN user_cnt ELSE NULL END) as 'D+155',
          MAX(CASE WHEN dt_plus = 156 THEN user_cnt ELSE NULL END) as 'D+156',
          MAX(CASE WHEN dt_plus = 157 THEN user_cnt ELSE NULL END) as 'D+157',
          MAX(CASE WHEN dt_plus = 158 THEN user_cnt ELSE NULL END) as 'D+158',
          MAX(CASE WHEN dt_plus = 159 THEN user_cnt ELSE NULL END) as 'D+159',
          MAX(CASE WHEN dt_plus = 160 THEN user_cnt ELSE NULL END) as 'D+160',
          MAX(CASE WHEN dt_plus = 161 THEN user_cnt ELSE NULL END) as 'D+161',
          MAX(CASE WHEN dt_plus = 162 THEN user_cnt ELSE NULL END) as 'D+162',
          MAX(CASE WHEN dt_plus = 163 THEN user_cnt ELSE NULL END) as 'D+163',
          MAX(CASE WHEN dt_plus = 164 THEN user_cnt ELSE NULL END) as 'D+164',
          MAX(CASE WHEN dt_plus = 165 THEN user_cnt ELSE NULL END) as 'D+165',
          MAX(CASE WHEN dt_plus = 166 THEN user_cnt ELSE NULL END) as 'D+166',
          MAX(CASE WHEN dt_plus = 167 THEN user_cnt ELSE NULL END) as 'D+167',
          MAX(CASE WHEN dt_plus = 168 THEN user_cnt ELSE NULL END) as 'D+168',
          MAX(CASE WHEN dt_plus = 169 THEN user_cnt ELSE NULL END) as 'D+169',
          MAX(CASE WHEN dt_plus = 170 THEN user_cnt ELSE NULL END) as 'D+170',
          MAX(CASE WHEN dt_plus = 171 THEN user_cnt ELSE NULL END) as 'D+171',
          MAX(CASE WHEN dt_plus = 172 THEN user_cnt ELSE NULL END) as 'D+172',
          MAX(CASE WHEN dt_plus = 173 THEN user_cnt ELSE NULL END) as 'D+173',
          MAX(CASE WHEN dt_plus = 174 THEN user_cnt ELSE NULL END) as 'D+174',
          MAX(CASE WHEN dt_plus = 175 THEN user_cnt ELSE NULL END) as 'D+175',
          MAX(CASE WHEN dt_plus = 176 THEN user_cnt ELSE NULL END) as 'D+176',
          MAX(CASE WHEN dt_plus = 177 THEN user_cnt ELSE NULL END) as 'D+177',
          MAX(CASE WHEN dt_plus = 178 THEN user_cnt ELSE NULL END) as 'D+178',
          MAX(CASE WHEN dt_plus = 179 THEN user_cnt ELSE NULL END) as 'D+179',
          MAX(CASE WHEN dt_plus = 180 THEN user_cnt ELSE NULL END) as 'D+180'

        FROM
          (SELECT 
            first_dt AS 'dt',
            dt_cnt AS 'dt_plus',
            COUNT(*) AS 'user_cnt'
          FROM
            (SELECT 
              a.holder,
              a.first_dt,
              b.login_dt,
              DATEDIFF(login_dt, first_dt) AS 'dt_cnt'
            FROM
              (SELECT 
                param2 AS 'holder',
                MIN(DATE_FORMAT(created_at, '%Y-%m-%d')) AS 'first_dt'
              FROM
                game_log
              WHERE
                created_at > '2023-05-25 12:46'
                AND type = 'login_user'
              GROUP BY 1) AS a
            INNER JOIN 
              (SELECT 
                param2 AS 'holder',
                DATE_FORMAT(created_at, '%Y-%m-%d') AS 'login_dt'
              FROM
                game_log
              WHERE
                created_at > '2023-05-25 12:46'
                AND type = 'login_user'
              GROUP BY 1 , 2) AS b ON a.holder = b.holder) AS c
          GROUP BY 1 , 2) AS d
        GROUP BY 1
        ORDER BY 1;
        '''
    );
    """
    return client.query(complex_query_1).result().to_dataframe()

def find_date_cell(worksheet, date):
    try:
        return worksheet.find(date)
    except gspread.exceptions.CellNotFound:
        return None

def get_excel_column(index):
    # Adjust the index to start from 'GA', which is the 182th column in Excel
    adjusted_index = index + 181  

    # Calculate the Excel column name
    if adjusted_index <= 26:
        # Single letter column
        return chr(64 + adjusted_index)
    else:
        # Double letter column
        first_letter_index = (adjusted_index - 1) // 26
        second_letter_index = (adjusted_index - 1) % 26
        first_letter = chr(64 + first_letter_index)
        second_letter = chr(65 + second_letter_index)
        return first_letter + second_letter

def update_sheet_with_complex_query_results(worksheet, results):
    # Initialize a list to keep track of cell updates
    cell_updates = []

    # Process each row in the filtered results
    for index, row in results.iterrows():
        # Find the cell for the date
        date_cell = find_date_cell(worksheet, row['dt'])
        if date_cell:
            # Prepare the updates for each cell in the row
            for col_idx, value in enumerate(row[1:], start=2):
                cell_range = f'{get_excel_column(col_idx)}{date_cell.row}'
                # Check if the column is beyond the limit of 'MX'
                if cell_range.startswith('MY'):
                    break  # Stop if the column exceeds the MX limit
                cell_updates.append({
                    'range': cell_range,
                    'values': [[value]]
                })

    request_times = []  # Store the times when requests are made

    for i in range(0, len(cell_updates), 30):
        now = time.time()  # Current time in seconds
        request_times = [t for t in request_times if now - t < 60]  # Keep only the last minute's requests

        if len(request_times) >= 55:  # If near the limit, wait
            time_to_wait = 61 - (now - request_times[0])
            logging.info(f"Approaching quota limit, waiting for {time_to_wait} seconds")
            time.sleep(time_to_wait)
            request_times = [t for t in request_times if now - t < 60]

        batch = cell_updates[i:i+30]
        try:
            worksheet.batch_update(batch, value_input_option='USER_ENTERED')
            logging.info(f"Updated cells from {batch[0]['range']} to {batch[-1]['range']}")
            request_times.append(time.time())  # Log the time of the request
        except APIError as e:
            if "Quota exceeded" in str(e):
                logging.info("Quota exceeded, adjusting batch size and retrying")
                # Implement logic to handle quota exceedance, such as reducing batch size
            else:
                raise

if __name__ == "__main__":
    update_retention_datas_in_sheets(None)

