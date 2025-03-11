import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from utils.aws.s3 import get_s3_client, write_markdown_to_s3

write_markdown_to_s3(get_s3_client(), '#This is a markdown\n##this is a simple markdown')