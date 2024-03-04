import base64
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from google.cloud import logging, storage
import os

def retrieve_and_save_logs(request):
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = f"{yesterday}T00:00:00Z"
    end_date = f"{yesterday}T23:59:59Z"

    project_id = os.getenv('GCP_PROJECT')
    log_storage_bucket = os.getenv('LOG_STORAGE_BUCKET')
    tracked_urls = [
        "https://somaz.cdn.link/Setup.exe",
        "https://somaz.cdn.link/Update.zip"
    ]

    client = logging.Client(project=project_id)
    storage_client = storage.Client()
    bucket = storage_client.bucket(log_storage_bucket)

    for url in tracked_urls:
        filter_str = f"""
        resource.type="http_load_balancer" AND
        httpRequest.requestUrl="{url}" AND
        timestamp>="{start_date}" AND
        timestamp<="{end_date}"
        """
        print(f"Retrieving logs for {url}")
        entries = list(client.list_entries(filter_=filter_str))

        # Sort entries by timestamp and deduplicate based on 1-minute proximity
        entries.sort(key=lambda x: x.timestamp)
        unique_entries = deduplicate_entries(entries)

        log_entries_count = len(unique_entries)  # Count unique log entries

        file_name_part = url.rsplit('/', 1)[-1].rsplit('.', 1)[0]
        summary_file_name = f"{file_name_part}_Download_Count.txt"
        summary_blob = bucket.blob(summary_file_name)

        # Generate and upload the summary
        upload_summary(summary_blob, yesterday, log_entries_count)

    return f"Processed logs for {len(tracked_urls)} URLs."

def deduplicate_entries(entries):
    unique_entries = []
    last_timestamp = None
    for entry in entries:
        entry_timestamp = entry.timestamp.replace(tzinfo=timezone.utc).timestamp()
        if not last_timestamp or entry_timestamp - last_timestamp > 60:  # More than 1 minute apart
            unique_entries.append(entry)
            last_timestamp = entry_timestamp
    return unique_entries

def upload_summary(blob, yesterday, count):
    existing_summary = blob.download_as_text() if blob.exists() else ""
    # Parse the existing summary
    daily_counts, monthly_totals = parse_existing_summary(existing_summary)

    # Update daily counts and monthly totals with year information
    daily_counts[yesterday] = count
    year = datetime.strptime(yesterday, '%Y-%m-%d').year  # Year extraction
    month_str = datetime.strptime(yesterday, '%Y-%m-%d').strftime('%B')  # Month extraction
    monthly_totals[f"{year}_{month_str}"] = monthly_totals.get(f"{year}_{month_str}", 0) + count  # Year-Month key used

    # Generate the updated summary
    final_summary = generate_final_summary(daily_counts, monthly_totals)

    blob.upload_from_string(final_summary)
    print(f"Updated summary in {blob.name}")

def parse_existing_summary(existing_summary):
    """
    Parses the existing summary into daily counts and monthly totals, expecting year-month keys for monthly totals.
    """
    daily_counts = {}
    monthly_totals = defaultdict(int)
    for line in existing_summary.split('\n'):
        if line.strip() and "Total_Count" not in line:
            date_str, count_str = line.split(':')
            daily_counts[date_str.strip()] = int(count_str.strip())
        elif "Total_Count" in line:
            year_month, total_str = line.split('_Total_Count:')
            monthly_totals[year_month.strip()] = int(total_str.strip())

    return daily_counts, monthly_totals

def generate_final_summary(daily_counts, monthly_totals):
    """
    Combines daily counts and monthly totals into a final summary string, using year-month keys for monthly totals.
    """
    # Sort daily counts by date
    sorted_daily_counts = dict(sorted(daily_counts.items(), key=lambda item: datetime.strptime(item[0], '%Y-%m-%d')))
    daily_counts_section = '\n'.join(f"{date}: {count}" for date, count in sorted_daily_counts.items())
    
    # No need to sort monthly_totals as keys are already in year_month format
    monthly_totals_section = '\n'.join(f"{year_month}_Total_Count: {total}" for year_month, total in monthly_totals.items())

    return f"{daily_counts_section}\n\n{monthly_totals_section}"