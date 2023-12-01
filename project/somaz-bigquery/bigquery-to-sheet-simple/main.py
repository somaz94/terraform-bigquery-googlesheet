import os
import gspread
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
import logging
from datetime import datetime, timedelta

def update_data_in_sheets(request):
    try:
        logging.info("Starting update_data_in_sheets function")

        # BigQuery setup
        client = bigquery.Client()
        dataset_id = os.getenv('BIGQUERY_DATASET', 'mgmt-2023.mongodb_dataset')

        # Connect to Google Sheets
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file('bigquery.json', scopes=scopes)
        gc = gspread.authorize(creds)
        logging.info("Connected to Google Sheets")

        # Open Google Sheets document
        sh = gc.open_by_key(os.getenv('SHEET_ID'))
        worksheet = sh.worksheet('Somaz_Table') # Replace 'Somaz_Table' with your actual sheet name

        # Determine yesterday's date
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Execute queries and update sheet
        update_sheet_with_query(client, worksheet, nru_query, yesterday, 'B', 'date') # NRU data in column B
        update_sheet_with_query(client, worksheet, dau_query, yesterday, 'D', 'dt')  # DAU data in column D
        update_sheet_with_query(client, worksheet, arena_finish_query, yesterday, 'G', 'date')  # 전투횟수 data in column G
        update_sheet_with_query(client, worksheet, arena_finish_rewards_query, yesterday, 'I', 'date')  # DP 칩 획득(아레나)(비귀속) data in column I
        update_sheet_with_query(client, worksheet, arena_ticket_consumption_query, yesterday, 'L', 'date') # DP칩 사용(비귀속) data in column L
        update_sheet_with_query(client, worksheet, character_gradeup_query, yesterday, 'M', 'date')  # 승급횟수 data in column M

        logging.info("Daily data updated in Google Sheets for yesterday!")
        return "Daily data updated in Google Sheets for yesterday!", 200

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return f"An error occurred: {e}", 500

def update_sheet_with_query(client, worksheet, query, date, column, date_column_name):
    # Fetching data from BigQuery
    results = client.query(query).result().to_dataframe()

    # Check if the date exists in the results
    if date not in results[date_column_name].values:
        # Date not found, insert 0
        try:
            # Find the row in the sheet where the date matches
            date_cell = worksheet.find(date)
            # Update the count in the corresponding row and column with 0
            cell = f'{column}{date_cell.row}'
            worksheet.update_acell(cell, 0)
            # Set the cell format to center align
            worksheet.format(cell, {"horizontalAlignment": "CENTER"})
        except gspread.exceptions.CellNotFound:
            logging.warning(f"Date {date} not found in the sheet.")
            return

    # Update data for specified date in Google Sheets
    for index, row in results.iterrows():
        if row[date_column_name] == date:
            try:
                # Find the row in the sheet where the date matches
                date_cell = worksheet.find(str(row[date_column_name]))
                # Update the count in the corresponding row and column
                cell = f'{column}{date_cell.row}'
                worksheet.update_acell(cell, row['count'])
                # Set the cell format to center align
                worksheet.format(cell, {"horizontalAlignment": "CENTER"})
            except gspread.exceptions.CellNotFound:
                logging.warning(f"Date {row[date_column_name]} not found in the sheet.")
                break

# Define queries here

# NRU data
nru_query = """
SELECT
  FORMAT_DATE("%Y-%m-%d", CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE)) AS date,
  COUNT(*) as count
FROM
  `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
WHERE
  reason = '/user/create'
  AND collectionName IN UNNEST(["create_user_detail"])
  AND (
    CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) BETWEEN DATE_TRUNC(CURRENT_DATE(), MONTH) AND CURRENT_DATE()
    OR
    CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) = LAST_DAY(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH)
  )
GROUP BY
  date
ORDER BY
  date;
"""

# DAU data
dau_query = """
WITH
  Step1 AS (
    SELECT
      PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS parsed_time,
      nid
    FROM
      `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
    WHERE
      reason = '/login'
      AND collectionName IN UNNEST(["login"])
      AND (
        CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) BETWEEN DATE_TRUNC(CURRENT_DATE(), MONTH) AND CURRENT_DATE()
        OR
        CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) = LAST_DAY(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH)
      )
  ),
  Step2 AS (
    SELECT
      FORMAT_DATE('%Y-%m-%d', parsed_time) AS dt,
      nid,
      COUNT(*) as count
    FROM
      Step1
    GROUP BY
      dt, nid
  )
SELECT
  dt,
  COUNT(nid) as count
FROM
  Step2
GROUP BY
  dt
ORDER BY
  dt;
"""

# 전투횟수 data
arena_finish_query = """
SELECT
  FORMAT_DATE("%Y-%m-%d", PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time)) AS date,
  COUNT(*) as count
FROM
  `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
WHERE
  reason = '/arena/finish'
  AND collectionName IN UNNEST(["finish_arena"])
  AND (
    CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) BETWEEN DATE_TRUNC(CURRENT_DATE(), MONTH) AND CURRENT_DATE()
    OR
    CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) = LAST_DAY(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH)
  )
GROUP BY
  date
ORDER BY
  date;
"""

# DP 칩 획득(아레나)(비귀속) data
arena_finish_rewards_query = """
WITH
  ParsedData AS (
    SELECT
      FORMAT_DATE("%Y-%m-%d", PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time)) AS date,
      JSON_EXTRACT_SCALAR(contents, '$.reward.dataId') AS dataId,
      CAST(JSON_EXTRACT_SCALAR(contents, '$.reward.quantity') AS INT64) AS quantity
    FROM
      `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
    WHERE
      reason = '/arena/finish'
      AND collectionName IN UNNEST(["payment_material"])
      AND (
        CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) BETWEEN DATE_TRUNC(CURRENT_DATE(), MONTH) AND CURRENT_DATE()
        OR
        CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) = LAST_DAY(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH)
      )
  )
SELECT
  date,
  SUM(quantity) AS count
FROM
  ParsedData
GROUP BY
  date
ORDER BY
  date;
"""

# DP칩 사용(비귀속) data
arena_ticket_consumption_query = """
WITH
  ParsedData AS (
    SELECT
      PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS time,
      CAST(JSON_EXTRACT_SCALAR(contents, '$.id') AS INT64) AS id,
      CAST(JSON_EXTRACT_SCALAR(contents, '$.beforeValue') AS INT64) AS beforeValue,
      CAST(JSON_EXTRACT_SCALAR(contents, '$.afterValue') AS INT64) AS afterValue
    FROM
      `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
    WHERE
      reason = '/user/arenaTicket/charge'
      AND collectionName IN UNNEST(["consume_material"])
      AND (
        CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) BETWEEN DATE_TRUNC(CURRENT_DATE(), MONTH) AND CURRENT_DATE()
        OR
        CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS DATE) = LAST_DAY(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH)
      )
  ),
  CalculatedData AS (
    SELECT
      FORMAT_DATE('%Y-%m-%d', time) AS date,
      id,
      beforeValue - afterValue AS quantity
    FROM
      ParsedData
  )
SELECT
  date,
  SUM(quantity) AS count
FROM
  CalculatedData
WHERE
  id = 403000
GROUP BY
  date
ORDER BY
  date;
"""

# 승급횟수 data
character_gradeup_query = """
SELECT
  FORMAT_DATE("%Y-%m-%d", PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time)) AS date,
  COUNT(*) as count
FROM
  `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
WHERE
  reason = '/character/gradeup'
  AND collectionName IN UNNEST(["grade_up_character"])
  AND (
    DATE(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time)) = LAST_DAY(CURRENT_DATE(), MONTH)
    OR
    DATE(PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time)) = LAST_DAY(CURRENT_DATE() - INTERVAL 1 MONTH, MONTH)
  )
GROUP BY
  date
ORDER BY
  date;
"""

if __name__ == "__main__":
    update_data_in_sheets(None) # Passing None since we're not using the request object
