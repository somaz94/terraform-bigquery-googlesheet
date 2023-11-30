import os
import gspread
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
import logging
from datetime import datetime, timedelta
import time

def update_multiple_datas_in_sheets(request):
    try:
        logging.info("Starting update_multiple_datas_in_sheets function")

        # BigQuery setup
        client = bigquery.Client()

        # Connect to Google Sheets
        creds = Credentials.from_service_account_file('bigquery.json', scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        gc = gspread.authorize(creds)
        logging.info("Connected to Google Sheets")

        # Open Google Sheets document
        sh = gc.open_by_key(os.getenv('SHEET_ID'))
        worksheet = sh.worksheet('Somaz_Table')  # Replace 'Somaz_Table' with your actual sheet name
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Execute and update for each query
        execute_and_update_for_query(client, worksheet, yesterday, complex_query_1(client), get_complex_query_1_mapping())
        time.sleep(10)
        execute_and_update_for_query(client, worksheet, yesterday, complex_query_2(client), get_complex_query_2_mapping())
        time.sleep(10)
        execute_and_update_for_query(client, worksheet, yesterday, complex_query_3(client), get_complex_query_3_mapping())
        time.sleep(10)
        execute_and_update_for_query(client, worksheet, yesterday, complex_query_4(client), get_complex_query_4_mapping())
        time.sleep(10)
        execute_and_update_for_query(client, worksheet, yesterday, complex_query_5(client), get_complex_query_5_mapping())

        # Add additional query executions here

        logging.info("Data from multiple queries updated in Google Sheets for yesterday!")
        return "Data from multiple queries updated in Google Sheets for yesterday!", 200
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return f"An error occurred: {e}", 500

def execute_and_update_for_query(client, worksheet, date, query, column_mapping):
    results = query
    for item_name, column in column_mapping.items():
        update_sheet_for_item(worksheet, results, item_name, column, date)

def update_sheet_for_item(worksheet, results, item_name, column, date):
    try:
        date_cell = worksheet.find(date)
        cell = f'{column}{date_cell.row}'

        if 'itemName' in results.columns:
            # This branch handles the structure from complex_query_1
            item_data = results[results['itemName'] == item_name]
            date_data = int(item_data['dates'].apply(lambda x: next((d['quantity'] for d in x if d['date'] == date), 0)).iloc[0]) if not item_data.empty else 0
        else:
            # This branch handles the structure from complex_query_2
            date_data = int(results[results['date'] == date][item_name].iloc[0]) if not results[results['date'] == date].empty else 0

        worksheet.update_acell(cell, date_data)
        worksheet.format(cell, {"horizontalAlignment": "CENTER"})
    except gspread.exceptions.CellNotFound:
        logging.warning(f"Date {date} not found in the sheet for item {item_name}.")

def complex_query_1(client):
    # Define and execute the complex query
    complex_query_1 = """
    WITH ParsedData AS (
        SELECT
            PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS time,
            CAST(JSON_EXTRACT_SCALAR(contents, '$.reward.dataId') AS INT64) AS dataId,
            CAST(JSON_EXTRACT_SCALAR(contents, '$.reward.quantity') AS INT64) AS quantity
        FROM
            `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
        WHERE
            reason = '/market/flower-shop/buy'
            AND collectionName IN UNNEST(["payment_material", "payment_hero_gacha"])
            AND PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
    ),
    ProcessedData AS (
        SELECT
            FORMAT_DATE('%Y-%m-%d', time) AS date,
            CASE
                WHEN dataId = 400000 THEN '소머즈 링크'
                WHEN dataId = 400001 THEN '소머즈 에일'

                WHEN dataId = 451000 THEN '하급 나무 승급서'
                WHEN dataId = 451010 THEN '하급 꽃 승급서'
                WHEN dataId = 451020 THEN '하급 곤충 승급서'

                WHEN dataId = 451001 THEN '중급 나무 승급서'
                WHEN dataId = 451011 THEN '중급 꽃 승급서'
                WHEN dataId = 451021 THEN '중급 곤충 승급서'

                ELSE 'Unknown Item'
            END AS itemName,
            quantity
        FROM ParsedData
    ),
    AggregatedData AS (
        SELECT
            itemName,
            date,
            SUM(quantity) AS quantity
        FROM ProcessedData
        GROUP BY itemName, date
    )
    SELECT
        itemName,
        ARRAY_AGG(STRUCT(date, quantity) ORDER BY date) AS dates,
        SUM(quantity) AS totalQuantity
    FROM AggregatedData
    GROUP BY itemName
    ORDER BY itemName;
    """
    return client.query(complex_query_1).result().to_dataframe()

def get_complex_query_1_mapping():
    # Map each item to its corresponding column in the sheet
    return {
        "소머즈 링크": "N",
        "소머즈 에일": "O",
        "하급 나무 승급서": "P",
        "하급 꽃 승급서": "Q",
        "하급 곤충 승급서": "R",
        "중급 나무 승급서": "V",
        "중급 꽃 승급서": "W",
        "중급 곤충 승급서": "X"

        # ... Add mappings for other items ...
    }

def complex_query_2(client):

    complex_query_2 = """
    WITH ParsedData AS (
        SELECT
            PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) AS time,
            JSON_EXTRACT_ARRAY(contents, '$.createCharacter') AS createCharacterArray,
            CAST(JSON_EXTRACT_SCALAR(contents, '$.usedGoods[0].id') AS INT64) AS id
        FROM
            `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
        WHERE
            reason = '/inventory/pack/reveal'
            AND collectionName IN UNNEST(["reveal_hero_gacha_pack"])
            AND PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
    ),
    UnwoundData AS (
        SELECT
            time,
            id,
            JSON_EXTRACT_SCALAR(char, '$.actorId') AS actorId
        FROM
            ParsedData
        CROSS JOIN
            UNNEST(createCharacterArray) AS char
    ),
    AggregatedData AS (
        SELECT
            FORMAT_DATE('%Y-%m-%d', time) AS date,
            SUM(CASE WHEN CAST(actorId AS INT64) BETWEEN 105001 AND 106000 THEN 1 ELSE 0 END) AS `커먼`,
            SUM(CASE WHEN CAST(actorId AS INT64) BETWEEN 104001 AND 105000 THEN 1 ELSE 0 END) AS `언커먼`,
            SUM(CASE WHEN CAST(actorId AS INT64) BETWEEN 103001 AND 104000 THEN 1 ELSE 0 END) AS `레어`,
            SUM(CASE WHEN CAST(actorId AS INT64) BETWEEN 102001 AND 103000 THEN 1 ELSE 0 END) AS `에픽`,
            SUM(CASE WHEN CAST(actorId AS INT64) BETWEEN 101001 AND 102000 THEN 1 ELSE 0 END) AS `레전드`
        FROM
            UnwoundData
        WHERE
            id IN (3400004, 3400005, 3400006, 3400007, 3400008)
        GROUP BY
            date
    )
    SELECT
        date,
        `커먼`,
        `언커먼`,
        `레어`,
        `에픽`,
        `레전드`
    FROM
        AggregatedData
    ORDER BY
        date;
    """
    return client.query(complex_query_2).result().to_dataframe()    

def get_complex_query_2_mapping():
    # Map each item to its corresponding column in the sheet
    return {
        "커먼": "AM",
        "언커먼": "AN",
        "레어": "AO",
        "에픽": "AP",
        "레전드": "AQ"

        # ... Add mappings for other items ...
    }

def complex_query_3(client):
    complex_query_3 = """
    WITH ParsedData AS (
        SELECT
            FORMAT_DATE('%Y-%m-%d', PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time)) AS date,
            CAST(JSON_EXTRACT_SCALAR(contents, '$.reward.dataId') AS INT64) AS dataId,
            CAST(JSON_EXTRACT_SCALAR(contents, '$.reward.quantity') AS INT64) AS quantity
        FROM
            `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
        WHERE
            reason = '/character/breeding'
            AND collectionName IN UNNEST(["payment_character"])
            AND PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
    )
    SELECT
        date,
        SUM(CASE WHEN dataId BETWEEN 105001 AND 106000 THEN quantity ELSE 0 END) AS `커먼`,
        SUM(CASE WHEN dataId BETWEEN 104001 AND 105000 THEN quantity ELSE 0 END) AS `언커먼`,
        SUM(CASE WHEN dataId BETWEEN 103001 AND 104000 THEN quantity ELSE 0 END) AS `레어`,
        SUM(CASE WHEN dataId BETWEEN 102001 AND 103000 THEN quantity ELSE 0 END) AS `에픽`,
        SUM(CASE WHEN dataId BETWEEN 101001 AND 102000 THEN quantity ELSE 0 END) AS `레전더리`
    FROM
        ParsedData
    GROUP BY
        date
    ORDER BY
        date;
    """
    return client.query(complex_query_3).result().to_dataframe()

def get_complex_query_3_mapping():
    return {
        "커먼": "AR",
        "언커먼": "AS",
        "레어": "AT",
        "에픽": "AU",
        "레전더리": "AV"
    }

def complex_query_4(client):
    complex_query_4 = """
    WITH ParsedData AS (
        SELECT
            FORMAT_DATE('%Y-%m-%d', PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time)) AS date,
            CAST(JSON_EXTRACT_SCALAR(contents, '$.usedCharacter.actorId') AS INT64) AS dataId
        FROM
            `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
        WHERE
            reason = '/character/gradeup'
            AND collectionName IN UNNEST(["consume_character"])
            AND PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
    )
    SELECT
        date,
        SUM(CASE WHEN dataId BETWEEN 105001 AND 106000 THEN 1 ELSE 0 END) AS `커먼`,
        SUM(CASE WHEN dataId BETWEEN 104001 AND 105000 THEN 1 ELSE 0 END) AS `언커먼`,
        SUM(CASE WHEN dataId BETWEEN 103001 AND 104000 THEN 1 ELSE 0 END) AS `레어`,
        SUM(CASE WHEN dataId BETWEEN 102001 AND 103000 THEN 1 ELSE 0 END) AS `에픽`,
        SUM(CASE WHEN dataId BETWEEN 101001 AND 102000 THEN 1 ELSE 0 END) AS `레전드`
    FROM
        ParsedData
    GROUP BY
        date
    ORDER BY
        date;
    """
    return client.query(complex_query_4).result().to_dataframe()

def get_complex_query_4_mapping():
    return {
        "커먼": "BL",
        "언커먼": "BM",
        "레어": "BN",
        "에픽": "BO",
        "레전드": "BP"
    }

def complex_query_5(client):
    complex_query_5 = """
    WITH ParsedData AS (
    SELECT
        FORMAT_DATE('%Y-%m-%d', PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time)) AS date,
        CAST(JSON_EXTRACT_SCALAR(contents, '$.usedCharacter.actorId') AS INT64) AS dataId
    FROM
        `somaz-bigquery.mongodb_dataset.production-mongodb-internal-table`
    WHERE
        reason = '/character/level/up'
        AND collectionName IN UNNEST(["consume_character"])
        AND PARSE_TIMESTAMP('%a %b %d %H:%M:%S UTC %Y', time) >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
    )
    SELECT
        date,
        SUM(CASE WHEN dataId BETWEEN 105001 AND 106000 THEN 1 ELSE 0 END) AS `커먼`,
        SUM(CASE WHEN dataId BETWEEN 104001 AND 105000 THEN 1 ELSE 0 END) AS `언커먼`,
        SUM(CASE WHEN dataId BETWEEN 103001 AND 104000 THEN 1 ELSE 0 END) AS `레어`,
        SUM(CASE WHEN dataId BETWEEN 102001 AND 103000 THEN 1 ELSE 0 END) AS `에픽`,
        SUM(CASE WHEN dataId BETWEEN 101001 AND 102000 THEN 1 ELSE 0 END) AS `레전드`
    FROM
        ParsedData
    GROUP BY
        date
    ORDER BY
        date;
    """
    return client.query(complex_query_5).result().to_dataframe()

def get_complex_query_5_mapping():
    return {
        "커먼": "BQ",
        "언커먼": "BR",
        "레어": "BS",
        "에픽": "BT",
        "레전드": "BU"
    }


if __name__ == "__main__":
    update_multiple_datas_in_sheets(None)

