import pathlib
from typing import Dict

import functions_framework
from google.cloud import bigquery

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def save_gcs_file_to_bq(cloud_event):

    try:
        print(f"Passing JSON arguments for GCF...")
        arguments = request.get_json(force=True)
        bq_dataset = escape(arguments["dataset"])  # required
        bq_table = escape(arguments["table"])  # required
        disposition = escape(arguments["disposition"])  # required
    except Exception as e:
        print(f"WARNING: Handling error in CF args passed - {e}")

    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    # table_id = "fake-news-bears.staging.tweets_score_hate"
    table_id = f"fake-news-bears.{bq_dataset}.{bq_table}"

    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket}")
    print(f"File: {name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")

    client = bigquery.Client()

    current_directory = pathlib.Path(__file__).parent
    schema_path = str(current_directory / f"schemas/{bq_table}.json")
    schema = client.schema_from_json(schema_path)

    job_config = bigquery.LoadJobConfig(
        schema=schema, skip_leading_rows=1, source_format=bigquery.SourceFormat.CSV
    )

    # Use a wildcard to concat multiple files in a bucket
    uri = f"gs://{bucket}/*"

    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()
    print("The GCS files were correctly loaded to BQ...")

    destination_table = client.get_table(table_id)  # Make an API request.
    print(f"Loaded {destination_table.num_rows} rows...")
