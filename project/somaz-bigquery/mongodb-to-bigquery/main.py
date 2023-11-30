import os
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from flask import jsonify

def start_dataflow(request):
    # HTTP requests are Flask Request objects, so you can use the object's methods to analyze the request data.
    # If you want to receive data as a POST request, or if you want to use another method, modify this part appropriately.
    
    # Importing Environment Variables
    PROJECT_ID = os.environ.get('PROJECT_ID')
    REGION = os.environ.get('REGION')
    SHARED_VPC = os.environ.get('SHARED_VPC')
    SUBNET_SHARE = os.environ.get('SUBNET_SHARE')
    SERVICE_ACCOUNT_EMAIL = os.environ.get('SERVICE_ACCOUNT_EMAIL')

    # Initialize Google Cloud SDK Authentication
    credentials = GoogleCredentials.get_application_default()

    # Creating API clients for Dataflow services
    service = build('dataflow', 'v1b3', credentials=credentials)

    databases = ["production"]  # List of your MongoDB databases

    responses = []

    for database in databases:
        # Setting Dataflow Job Parameters
        # https://cloud.google.com/dataflow/docs/reference/rest/v1b3/projects.locations.flexTemplates/launch
        # https://cloud.google.com/dataflow/docs/guides/templates/provided/mongodb-to-bigquery?hl=ko#api
        # https://console.cloud.google.com/storage/browser/_details/dataflow-templates/latest/flex/MongoDB_to_BigQuery;tab=live_object?hl=ko
        job_parameters = {
            "launchParameter": {
                "jobName": f"{database}-to-bigquery-job",
                "parameters": {
                    "mongoDbUri": f"mongodb://mongo:somaz!2023@34.11.11.111:27017", # mongodb://<DB id>:<DB Password>@<DB IP>:<DB Port>
                    "database": database,
                    "collection": "mongologs",
                    "outputTableSpec": f"{PROJECT_ID}:mongodb_dataset.{database}-mongodb-internal-table",
                    "userOption": "FLATTEN"
                },
                "environment": {
                    "tempLocation": "gs://bigquery-sheet-cloud-function-storage/tmp",
                    "network": SHARED_VPC,
                    "subnetwork": f"regions/{REGION}/subnetworks/{SUBNET_SHARE}-mgmt-b",
                    "serviceAccountEmail": SERVICE_ACCOUNT_EMAIL
                },
                "containerSpecGcsPath": 'gs://dataflow-templates/latest/flex/MongoDB_to_BigQuery'
            }
        }

    # error handling
        try:
            # Starting Dataflow Job
            request = service.projects().locations().flexTemplates().launch(
                projectId=PROJECT_ID,
                location=REGION,
                body=job_parameters
            )
            response = request.execute()
            responses.append(response)

        except Exception as e:
            print(f"Error occurred while processing {database}: {e}")
            responses.append({"database": database, "error": str(e)})

    return jsonify(responses)


