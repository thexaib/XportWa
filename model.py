# -*- coding: utf-8 -*-
import sys, re, os, string, datetime, time, sqlite3, glob, webbrowser, base64, subprocess, pprint

################################################################################
#Class Chatsession
class Chatsession:

    # init
    def __init__(self, id=None, contactname=None, contactid=None,
                 msgcount=None, unreadcount=None, contactstatus=None, lastmessagedate=None,mode="Android"):

        # if invalid params are passed, sets attributes to invalid values
        # primary key
        if id == "" or id is None:
            self.id = -1
        else:
            self.id = id

        # contact nick
        if contactname == "" or contactname is None:
            self.contact_name = "N/A"
        else:
            self.contact_name = contactname

        # contact id
        if contactid == "" or contactid is None:
            self.contact_id = "N/A"
        else:
            self.contact_id = contactid

        # contact msg counter
        if msgcount == "" or msgcount is None:
            self.msg_count = "N/A"
        else:
            self.msg_count = msgcount

        # contact unread msg
        if unreadcount == "" or unreadcount is None:
            self.unread_count = "N/A"
        else:
            self.unread_count = unreadcount

        # contact status
        if contactstatus == "" or contactstatus is None:
            self.contact_status = "N/A"
        else:
            self.contact_status = contactstatus

        # contact last message date
        if lastmessagedate == "" or lastmessagedate is None or lastmessagedate == 0:
            self.last_message_date = " N/A" #space is necessary for that the empty chats are placed at the end on sorting
        else:
            try:
                if mode == "IPhone":
                    lastmessagedate = str(lastmessagedate)
                    if lastmessagedate.find(".") > -1: #if timestamp is not like "304966548", but like "306350664.792749", then just use the numbers in front of the "."
                        lastmessagedate = lastmessagedate[:lastmessagedate.find(".")]
                    self.last_message_date = datetime.datetime.fromtimestamp(int(lastmessagedate)+11323*60*1440)
                elif mode == "Android":
                    msgdate = str(lastmessagedate)
                    # cut last 3 digits (microseconds)
                    msgdate = msgdate[:-3]
                    self.last_message_date = datetime.datetime.fromtimestamp(int(msgdate))
                self.last_message_date = str( self.last_message_date )
            except (TypeError, ValueError) as msg:
                print('Error while reading chat #{}: {}'.format(self.id, msg))
                self.last_message_date = " N/A error"

        # chat session messages
        self.msg_list = []

    # comparison operator
    def __cmp__(self, other):
        if self.id == other.id:
            return 0
        return 1
#end:Class Chatsession
#############################


################################################################################
# Message Class definition
class Message:

    # init
    def __init__(self, id=None, fromme=None, msgdate=None, text=None, contactfrom=None, msgstatus=None,
                 localurl=None, mediaurl=None, mediathumb=None, mediathumblocalurl=None, mediawatype=None, mediasize=None, latitude=None, longitude=None, vcardname=None, vcardstring=None, parentmsg=None,mode="Android"):

        # if invalid params are passed, sets attributes to invalid values
        # primary key
        if id == "" or id is None:
            self.id = -1
        else:
            self.id = id

        # "from me" flag
        if fromme == "" or fromme is None:
            self.from_me = -1
        else:
            self.from_me = fromme

        # message timestamp
        if msgdate == "" or msgdate is None or msgdate == 0:
            self.msg_date = "N/A"
        else:
            try:
                if mode == "IPhone":
                    msgdate = str(msgdate)
                    if msgdate.find(".") > -1: #if timestamp is not like "304966548", but like "306350664.792749", then just use the numbers in front of the "."
                        msgdate = msgdate[:msgdate.find(".")]
                    self.msg_date = datetime.datetime.fromtimestamp(int(msgdate)+11323*60*1440)
                elif mode == "Android":
                    msgdate = str(msgdate)
                    # cut last 3 digits (microseconds)
                    msgdate = msgdate[:-3]
                    self.msg_date = datetime.datetime.fromtimestamp(int(msgdate))
            except (TypeError, ValueError) as msg:
                print('Error while reading message #{}: {}'.format(self.id, msg))
                self.msg_date = "N/A error"

        # message text
        if text == "" or text is None:
            self.msg_text = "N/A"
        else:
            self.msg_text = text
        # contact from
        if contactfrom == "" or contactfrom is None:
            self.contact_from = "N/A"
        else:
            self.contact_from = contactfrom

        # media
        if localurl == "" or localurl is None:
            self.local_url = ""
        else:
            self.local_url = localurl
        if mediaurl == "" or mediaurl is None:
            self.media_url = ""
        else:
            self.media_url = mediaurl
        if mediathumb == "" or mediathumb is None:
            self.media_thumb = ""
        else:
            self.media_thumb = mediathumb
        if mediathumblocalurl == "" or mediathumblocalurl is None:
            self.media_thumb_local_url = ""
        else:
            self.media_thumb_local_url = mediathumblocalurl
        if mediawatype == "" or mediawatype is None:
            self.media_wa_type = ""
        else:
            self.media_wa_type = mediawatype
        if mediasize == "" or mediasize is None:
            self.media_size = ""
        else:
            self.media_size = mediasize

        #status
        if msgstatus == "" or msgstatus is None:
            self.status = "N/A"
        else:
            self.status = msgstatus

        #GPS
        if latitude == "" or latitude is None:
            self.latitude = ""
        else:
            self.latitude = latitude
        if longitude == "" or longitude is None:
            self.longitude = ""
        else:
            self.longitude = longitude

        #VCARD
        if vcardname == "" or vcardname is None:
            self.vcard_name = ""
        else:
            self.vcard_name = vcardname
        if vcardstring == "" or vcardstring is None:
            self.vcard_string = ""
        else:
            self.vcard_string = vcardstring

        if parentmsg=="" or parentmsg is None:
            self.parent_msg="0"
        else:
            self.parent_msg=parentmsg


    # comparison operator
    def __cmp__(self, other):
        if self.id == other.id:
            return 0
        return 1
#end: Message Class definition
################################################################################

#class XporterOptions
class XportOptions:
    def __init__(self):
        pass


#Class: Xporter Base Class
#Class: Xporter Base Class
class Xporter(object):
    def __init__(self,mode):
        self.mode=mode
        self.dbfile=""
        self.wafile=None

        self.PYTHON_VERSION = None
        testtext = ""
        testtext = testtext.replace('\ue40e', 'v3')
        if testtext == "v3":
            self.PYTHON_VERSION = 3
            print ("Python Version 3.x")
        else:
            self.PYTHON_VERSION = 2
            print ("Python Version 2.x")
            reload(sys)
            sys.setdefaultencoding( "utf-8" )
            #import convert_smileys_python_2


    def initdb(self):
        self.msgstore = sqlite3.connect(self.dbfile)
        self.msgstore.row_factory = sqlite3.Row
        self.msgstorecur1 = self.msgstore.cursor()
        self.msgstorecur2 = self.msgstore.cursor()
        print "{} Connecting DB".format(self.mode)

    def trydecryptdb(self):
        pass

    def getAllChats(self):
        pass

#end:Class: Xporter Base Class

#Class: XporterAndroid
class XporterAndroid(Xporter):
    def __init__(self):
        super(self.__class__,self).__init__(mode="Android")

    def trydecryptdb(self):
        self.repairedfile = ""
        self.decodedfile = ""
        try:
            self.msgstorecur1.execute("SELECT * FROM chat_list")
        except sqlite3.Error as msg:
            try:
                print ("trying to repair android database...")
                self.msgstorecur1.close()
                self.msgstorecur2.close()
                self.msgstore.close()
                self.repairedfile = self.dbfile+ "_repaired.db"
                if os.path.exists(self.repairedfile):
                    os.remove(self.repairedfile)
                os.system('echo .dump | sqlite3 "%s" > Temp.sql' % self.dbfile)
                os.system('echo .quit | sqlite3 -init Temp.sql "%s"' % self.repairedfile)
                if os.path.exists("Temp.sql"):
                    os.remove("Temp.sql")
                self.msgstore = sqlite3.connect(self.repairedfile)
                self.msgstore.row_factory = sqlite3.Row
                self.msgstorecur1 = self.msgstore.cursor()
                self.msgstorecur2 = self.msgstore.cursor()
                self.msgstorecur1.execute("SELECT * FROM chat_list")
            except sqlite3.Error as msg:
                try:
                    print ("trying to decrypt android database...")
                    self.msgstorecur1.close()
                    self.msgstorecur2.close()
                    self.msgstore.close()
                    if os.path.exists(self.repairedfile):
                        os.remove(self.repairedfile)
                    from Crypto.Cipher import AES
                    code = "346a23652a46392b4d73257c67317e352e3372482177652c"
                    if self.PYTHON_VERSION == 2:
                        code = code.decode('hex')
                    elif self.PYTHON_VERSION == 3:
                        code = bytes.fromhex(code)
                    cipher = AES.new(code,1)
                    decoded = cipher.decrypt(open(self.dbfile,"rb").read())
                    self.decodedfile = self.dbfile.replace(".db.crypt","")+".plain.db"
                    output = open(self.decodedfile,"wb")
                    output.write(decoded)
                    output.close()
                    #print ("size:" + str(len (decoded)) )
                    self.msgstore = sqlite3.connect(self.decodedfile)
                    self.msgstore.row_factory = sqlite3.Row
                    self.msgstorecur1 = self.msgstore.cursor()
                    self.msgstorecur2 = self.msgstore.cursor()
                    print ("decrypted database written to "+self.decodedfile)
                    self.msgstorecur1.execute("SELECT * FROM chat_list")
                except sqlite3.Error as msg:
                    try:
                        if os.path.exists(self.decodedfile):
                            print ("trying to repair decrypted android database...")
                            self.msgstorecur1.close()
                            self.msgstorecur2.close()
                            self.msgstore.close()
                            self.repairedfile = self.decodedfile + "_repaired.db"
                            if os.path.exists(self.repairedfile):
                                os.remove(self.repairedfile)
                            os.system('echo .dump | sqlite3 "%s" > Temp.sql' % self.decodedfile)
                            os.system('echo .quit | sqlite3 -init Temp.sql "%s"' % self.repairedfile)
                            if os.path.exists("Temp.sql"):
                                os.remove("Temp.sql")
                            self.msgstore = sqlite3.connect(self.repairedfile)
                            self.msgstore.row_factory = sqlite3.Row
                            self.msgstorecur1 = self.msgstore.cursor()
                            self.msgstorecur2 = self.msgstore.cursor()
                            self.msgstorecur1.execute("SELECT * FROM chat_list")
                    except sqlite3.Error as msg:
                        print("Could not open database file. Guess it's not a valid Android or Iphone database file. ")
                        try:
                            self.msgstorecur1.close()
                            self.msgstorecur2.close()
                            self.msgstore.close()
                            if os.path.exists(self.repairedfile):
                                os.remove(self.repairedfile)
                                #if os.path.exists(decodedfile):
                                #    os.remove(decodedfile)
                        except:
                            print('Could not clean up.')
                        sys.exit(1)
                except ValueError as msg:
                    print('Error during decrypting: {}'.format(msg))
                    print("Could not decrypt database file. Guess it's not a valid Android/Iphone database file or Whatsapp changed the encryption.")
                    sys.exit(1)

    def initdb(self):
        super(self.__class__,self).initdb()
        self.wastore = sqlite3.connect(self.wafile)
        self.wastore.row_factory = sqlite3.Row
        self.wastorecur = self.wastore.cursor()
        print "Connecting Wa file"

    def getAllChats(self):
        print("Getting Chat Sessions")
        chat_session_list = []
        try:
            if self.wafile is not None:
                self.wastorecur.execute("SELECT * FROM wa_contacts WHERE is_whatsapp_user = 1 GROUP BY jid")
                for ws in self.wastorecur:
                    #pprint.pprint(ws.keys())
                    break
                for chats in self.wastorecur:
                    # ------------------------------------------ #
                    #  ANDROID WA.db file *** wa_contacts TABLE  #
                    # ------------------------------------------ #
                    # chats[0] --> id (primary key)
                    # chats[1] --> jid
                    # chats[2] --> is_whatsapp_user
                    # chats[3] --> is_iphone
                    # chats[4] --> status
                    # chats[5] --> number
                    # chats[6] --> raw_contact_id
                    # chats[7] --> display_name
                    # chats[8] --> phone_type
                    # chats[9] --> phone_label
                    # chats[10] -> unseen_msg_count
                    # chats[11] -> photo_ts
                    try:
                        self.msgstorecur2.execute("SELECT message_table_id FROM chat_list WHERE key_remote_jid=?", [chats["jid"]])
                        lastmessage = self.msgstorecur2.fetchone()[0]
                        #!todo alternativ maximale _id WHERE key_remote_jid
                        self.msgstorecur2.execute("SELECT timestamp FROM messages WHERE _id=?", [lastmessage])
                        lastmessagedate = self.msgstorecur2.fetchone()[0]
                    except: #not all contacts that are whatsapp users may already have been chatted with
                        lastmessagedate = None

                    total_num=self.get_msg_count_by_chatid(chats["jid"])
                    curr_chat = Chatsession(id=chats["_id"],
                                            contactname=chats["display_name"],
                                            contactid=chats["jid"],
                                            msgcount=total_num,
                                            unreadcount=chats["unseen_msg_count"],
                                            contactstatus=chats["status"],
                                            lastmessagedate=lastmessagedate,
                                            mode=self.mode)

                    if total_num>0:
                        #chat_session_list[chats["_id"]]=curr_chat
                        chat_session_list.append(curr_chat)
                    #end:if not wafile
            else:
                self.msgstorecur1.execute("SELECT * FROM chat_list")
                for chats in self.msgstorecur1:
                    # ---------------------------------------------- #
                    #  ANDROID MSGSTORE.db file *** chat_list TABLE  #
                    # ---------------------------------------------- #
                    # chats[0] --> _id (primary key)
                    # chats[1] --> key_remote_jid (contact jid or group chat jid)
                    # chats[2] --> message_table_id (id of last message in this chat, corresponds to table messages primary key)
                    name = chats["key_remote_jid"].split('@')[0]
                    try:
                        lastmessage = chats["message_table_id"]
                        self.msgstorecur2.execute("SELECT timestamp FROM messages WHERE _id=?", [lastmessage])
                        lastmessagedate = self.msgstorecur2.fetchone()[0]
                    except:
                        lastmessagedate = None

                    total_num=self.get_msg_count_by_chatid(chats["jid"])
                    curr_chat = Chatsession(id=chats["_id"],
                                            contactname=name,
                                            contactid=chats["key_remote_jid"],
                                            msgcount=total_num,
                                            unreadcount=None,
                                            contactstatus=None,
                                            lastmessagedate=lastmessagedate,
                                            mode=self.mode)
                    if total_num>0:
                        chat_session_list.append(curr_chat)
                        #chat_session_list[chats["_id"]]=curr_chat

                        #end else no wafile

            chat_session_list = sorted(chat_session_list, key=lambda Chatsession: Chatsession.last_message_date, reverse=True)
            return chat_session_list
            #end try
        except sqlite3.Error as msg:
            print('Error: {}'.format(msg))
            sys.exit(1)

    def get_msg_count_by_chatid(self,chat_id):
        cur=self.msgstore.cursor()
        total=None
        cur.execute("SELECT count(*) as num FROM messages WHERE key_remote_jid=? ORDER BY _id ASC;", [chat_id])
        for ws in cur:
            total= ws['num']
            break
        return total

#endClass: XporterAndroid

#Class: XporterIPhone
class XporterIPhone(Xporter):
    def __init__(self):
        super(self.__class__,self).__init__(mode="IPhone")

    def trydecryptdb(self):
        try:
            # ------------------------------------------------------ #
            #  IPHONE  ChatStorage.sqlite file *** Z_METADATA TABLE  #
            # ------------------------------------------------------ #
            # Z_VERSION INTEGER PRIMARY KEY
            # Z_UIID VARCHAR
            # Z_PLIST BLOB
            from bplist import BPlistReader
            self.msgstorecur1.execute("SELECT * FROM Z_METADATA")
            metadata = self.msgstorecur1.fetchone()
            print ("*** METADATA PLIST DUMP ***\n")
            print ("Plist ver.:  {}".format(metadata["Z_VERSION"]))
            print ("UUID:        {}".format(metadata["Z_UUID"]))
            bpReader = BPlistReader(metadata["Z_PLIST"])
            plist = bpReader.parse()

            for entry in plist.items():
                if entry[0] == "NSStoreModelVersionHashes":
                    print ("{}:".format(entry[0]))
                    for inner_entry in entry[1].items():
                        print ("\t{}: {}".format(inner_entry[0],base64.b64encode(inner_entry[1]).decode("utf-8")))
                else:
                    print ("{}: {}".format(entry[0],entry[1]))
            print ("\n***************************\n")

        except:
            print ("Metadata Plist Dump is failed. Note that you need to use Python 2.7 for that bplist.py works")



#Class: XporterIPhone