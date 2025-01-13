
from services_handle.s3_operations import *

from services_handle.s3_operations import download_file
create_bucket("esther2026")
upload_file("/Users/ihc/Downloads/Losss.png", "esther2025")

delete_bucket("esther2026")

upload_file(file_path="Losss.png", bucket_name="esther2026", object_name="projects/dev/esther2026.png")

