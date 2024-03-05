import os
from google.cloud import bigquery

def remove_duplicates(request):
    # Initialize Bigquery Client
    client = bigquery.Client()

    PROJECT_ID = os.environ.get('PROJECT_ID')

    database = "production"  # Set up a database

    # Formatting a query string using an f-string
    query = f"""
    DELETE
    FROM `{PROJECT_ID}.mongodb_dataset.{database}-mongodb-internal-table`
    WHERE STRUCT(_id, timestamp) NOT IN (
      SELECT AS STRUCT _id, MAX(timestamp) as timestamp
      FROM `{PROJECT_ID}.mongodb_dataset.{database}-mongodb-internal-table`
      GROUP BY _id
    )
    """

    # Start Query
    query_job = client.query(query)

    # Wait for completion
    query_job.result()

    return 'Duplicates have been removed.'
