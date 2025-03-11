from datetime import datetime
from typing import Dict, Any
import snowflake.connector as sf
import os

def sf_connector():
    """Establishes a connection to Snowflake using environment variables."""
    try:
        conn = sf.connect(
            user=os.getenv('SF_USER'),
            password=os.getenv('SF_PASSWORD'),
            account=os.getenv('SF_ACCOUNT'),
            warehouse=os.getenv('SF_WAREHOUSE'),
            database=os.getenv('SF_DB'),
            role=os.getenv('SF_ROLE'),
            private_key_file='rsa_key.p8'  # Fetch the private key file path from env
        )
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        return None
    return conn

# Function to read from Snowflake (retrieves markdown based on URL and model)
def sf_litellm_read(url: str, model: str, type: str) -> str | None:
    try:
        conn = sf_connector()  
        if conn is None:
            print("Failed to connect to Snowflake.")
            return None
        cursor = conn.cursor()
        try:
            # Construct the SQL query
            query = f"""
                SELECT markdown 
                FROM litellm.public.LITELLM_LOGS 
                WHERE source = %s AND model = %s AND type = %s LIMIT 1
            """     
            # Execute the query
            cursor.execute(query, (url, model, type))
            # Fetch the result
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the markdown column
            else:
                return None  # No result found for the given URL and model
        except Exception as e:
            print(f"Error during the query execution: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        return None


def sf_litellm_write(data: Dict[str, Any]) -> bool:    
    try:
        conn = sf_connector()  
        if conn is None:
            print("Failed to connect to Snowflake.")
            return False
        cursor = conn.cursor()
        try:
            query = f"""
                INSERT INTO litellm.public.LITELLM_LOGS 
                (id, source, prompt, markdown, model, prompt_tokens, completion_tokens, created, type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Prepare the data for insertion
            values = (
                data["id"],
                data["source"],
                data["prompt"],
                data["markdown"],
                data["model"],
                data["prompt_tokens"],
                data["completion_tokens"],
                data["created"],
                data["type"]
            )
            
            # Execute the insert query
            cursor.execute(query, values)
            conn.commit()  # Commit the transaction
            return True
        except Exception as e:
            print(f"Error during the insert execution: {e}")
            conn.rollback()  # Rollback in case of error
            return False
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        return False
