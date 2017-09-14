from model import Chatsession
from model import Message
from model import XporterAndroid
from model import XporterIPhone

import sys, re, os, string, datetime, time, sqlite3, glob, webbrowser, base64, subprocess
from argparse import ArgumentParser
import pprint
from outlet import *

#func:checkplatform
def checkplatform(file):
    mode=""
    msgstore = sqlite3.connect(options.infile)
    msgstore.row_factory = sqlite3.Row
    cur=msgstore.cursor()
    try:
        cur.execute("SELECT * FROM ZWACHATSESSION")
        # if succeeded --> IPHONE mode
        mode = "IPone"
    except:
        # if failed --> ANDROID mode
        mode = "Android"

    cur.close()
    msgstore.close()
    return mode
#end:func:checkplatform


# parser options
parser = ArgumentParser(description='Exports a Whatsapp Chat from database to HTML.')
parser.add_argument(dest='infile',
                    help="input 'msgstore.db' or 'msgstore.db.crypt' (Android) or 'ChatStorage.sqlite' (iPhone) file to scan")
parser.add_argument('-w', '--wafile', dest='wafile',
                    help="optionally input 'wa.db' (Android) file to scan")
parser.add_argument('-o', '--outfile',  dest='outfile',
                    help="optionally choose name of output file")
parser.add_argument('-i', '--id', type=int, dest='chat_id',
                    help="for single chat id ",default=-1)


options = parser.parse_args()

# checks for the wadb file
if options.wafile is None:
    have_wa = False
elif not os.path.exists(options.wafile):
    print('"{}" file is not found!'.format(options.wafile))
    sys.exit(1)
else:
    have_wa = True

# checks for the input file
if options.infile is None:
    parser.print_help()
    sys.exit(1)
if not os.path.exists(options.infile):
    print('"{}" file is not found!'.format(options.infile))
    sys.exit(1)

#end:parsing thing


if checkplatform(options.infile)=="Android":
    xporter=XporterAndroid()
    if have_wa:
        xporter.wafile=options.wafile

    print "Android Mode "

else:
    xporter=XporterIPhone()
    print "IPhone Mode"

#setting up xporter
xporter.dbfile=options.infile
xporter.initdb()
xporter.trydecryptdb()
#end:setting up xporter


chats=xporter.getAllChats()

if options.chat_id is not -1:
    #get_msgs_for_chat
    #print_chatsessions({options.chat_id:chat_session_list[options.chat_id]})
    #msgs= get_msgs_for_chat(chat_session_list[options.chat_id])
    #print_msgs(msgs)
    pass
else:
    print_chats(chats)
