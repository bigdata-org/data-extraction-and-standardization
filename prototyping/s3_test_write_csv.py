import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from utils.aws.s3 import get_s3_client, write_dataframe_to_s3

df = pd.DataFrame([{'name':'xyz','age':'18'},{'name':'abc','age':'28'}])

write_dataframe_to_s3(get_s3_client(), df)