import socket
import streamlit as st

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def prettify_on(df, column):
    return df[df[column].apply(lambda x: '(Error)' not in x)]            
            