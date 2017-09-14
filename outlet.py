from model import Chatsession
from model import Message


def print_chats(list):
    print "{: >4} {: >40} {: >10}".format("id","Name","Messages")
    for i in list:
        print "{: >4} {: >40} {: >10}".format(i.id,i.contact_name,i.msg_count)
