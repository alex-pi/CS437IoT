from managers import ThingsManager
import time
from common import *

tm = ThingsManager()
def create():
    for sq in NUM_SEQ:
        tm.create_thing(seq_num=sq)
        tm.attach_certificate(seq_num=sq)

def delete():
    for sq in NUM_SEQ:
        tm.delete_certificate(seq_num=sq)
        tm.delete_thing(seq_num=sq)


create()
#delete()