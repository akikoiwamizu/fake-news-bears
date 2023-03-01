import functions_framework

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def gcs_to_bq(cloud_event):
   data = cloud_event.data

   event_id = cloud_event["id"]
   event_type = cloud_event["type"]

   bucket = data["bucket"]
   name = data["name"]
   metageneration = data["metageneration"]
   timeCreated = data["timeCreated"]
   updated = data["updated"]

   print(f"Event ID: {event_id}")
   print(f"Event type: {event_type}")
   print(f"Bucket: {bucket}")
   print(f"File: {name}")
   print(f"Metageneration: {metageneration}")
   print(f"Created: {timeCreated}")
   print(f"Updated: {updated}")
