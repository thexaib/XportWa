from model import Chatsession
from model import Message


def print_chats(list):
    print "{: >4} {: >40} {: >10}".format("id","Name","Messages")
    for idx, val in enumerate(list):
        print "{: >4} {: >40} {: >10}".format(idx,val.contact_name,val.msg_count)

def print_msgs(msgs):
    print "{: >4} {: >4} {: >60} {:>6} {:>6}".format("id","Sent","Message","Type","Parent")
    for m in msgs:
        print "{: >4} {: >4} {: >60} {:>6} {:>6}".format(m.id,m.from_me,m.msg_text[0:60],str(m.msg_type),m.parent_msg)
