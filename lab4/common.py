import os
import pandas as pd
import errno

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.abspath(os.path.join(ROOT_DIR, os.pardir))
CERTS_DIR = os.path.join(ROOT_DIR, 'certificates')
DATA_PATH = os.path.join(ROOT_DIR, 'data')

cert_format = "lab4_thing_{}.certificate.pem"
cert_id_format = "lab4_thing_{}.certificate.id"
pri_key_format = "lab4_thing_{}.private.key"
pub_key_format = "lab4_thing_{}.public.key"
grp_cert_format = "{}_CA_.crt"
data_file =  "vehicle{}.csv"

GROUP_NAME = 'Lab4_Group'
NAME_FORMAT = "lab4_thing_{}"
DEFAULT_POLICY = "Lab4_Policy1"
NUM_SEQ = [n for n in range(1, 6)]

GROUP_CA_PATH = "./groupCA/"
MAX_DISCOVERY_RETRIES = 10

def get_data(thing_num):
    return pd.read_csv(os.path.join(DATA_PATH, data_file.format(thing_num-1)))

def get_name(thing_num):
    return NAME_FORMAT.format(thing_num)

# Naive logger functions
LOG_LEVELS = {
    'ERROR': 0,
    'INFO': 1,
    'DEBUG': 2,
    'TRACE': 3
}

LOG_LVL = 'TRACE'

def trace(message):
    if LOG_LEVELS['TRACE'] <= LOG_LEVELS[LOG_LVL]:
        print(message)

def debug(message):
    if LOG_LEVELS['DEBUG'] <= LOG_LEVELS[LOG_LVL]:
        print(message)

def info(message):
    if LOG_LEVELS['INFO'] <= LOG_LEVELS[LOG_LVL]:
        print(message)