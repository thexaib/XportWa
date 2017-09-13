import sys, re, os, string, datetime, time, sqlite3, glob, webbrowser, base64, subprocess

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
        if self.id == other.pk_cs:
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
        if self.id == other.pk_msg:
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

    def initdb(self):
        self.msgstore = sqlite3.connect(self.dbfile)
        self.msgstore.row_factory = sqlite3.Row
        self.msgstorecur1 = self.msgstore.cursor()
        self.msgstorecur2 = self.msgstore.cursor()
        print "{} Connecting DB".format(self.mode)
#end:Class: Xporter Base Class

#Class: XporterAndroid
class XporterAndroid(Xporter):
    def __init__(self):
        super(self.__class__,self).__init__(mode="Android")

    def initdb(self):
        super(self.__class__,self).initdb()
#endClass: XporterAndroid

#Class: XporterIPhone
class XporterIPhone(Xporter):
    def __init__(self):
        super(self.__class__,self).__init__(mode="IPhone")

#Class: XporterIPhone