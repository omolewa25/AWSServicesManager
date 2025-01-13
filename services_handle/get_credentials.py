import os
from dotenv import load_dotenv

load_dotenv()


def credentials():

    return {"AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_REGION": os.getenv("REGION")}