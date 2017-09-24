from model import XporterAndroid
from model import XporterIPhone

import sys, os, sqlite3
from argparse import ArgumentParser
from outlet import *
import os
import sqlite3
import sys
from argparse import ArgumentParser

from model import XporterAndroid
from model import XporterIPhone
from outlet import *
from htmlout import *

#pathlib2

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
parser.add_argument('-d', '--id', dest='chat_id',
                    help="Comma separated list of chat ids ",default="")

parser.add_argument('-s','--isolate',action='store_true',dest='isolate',help='separate or isolate chat media into its own folder by copying media files',default=False)
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

#folder name if any of infile
infolder=""
if len(options.infile.split(os.sep)) >1:
    infolder_list=options.infile.split(os.sep)[:-1]
    infolder=os.sep.join(infolder_list)
    if not os.path.exists(infolder):
        print "{} folder not found".format(infolder)
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


chats=xporter.get_all_chats()

list_ids=[]
if options.chat_id!='':
    list_ids=str(options.chat_id).split(',')

if len(list_ids)>0:
    for id in list_ids:
        #get_msgs_for_chat
        msgs=xporter.get_all_msgs(int(id))
        #print_msgs(msgs)
        outfilename=None
        if options.outfile is not None:
            if len(list_ids)==1:
                outfilename=options.outfile+".html"
            else:
                outfilename=options.outfile+"_"+id+".html"
        report_html(chats[int(id)],msgs,infolder=infolder,outfile=outfilename,isolate=options.isolate)

else:
    print_chats(chats)
