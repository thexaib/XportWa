from model import Chatsession
from model import Message
import sys, re, os, string, datetime, time, sqlite3, glob, webbrowser, base64, subprocess
import fnmatch

######################################
#get_all_media_files
_allfiles_names=[]
_allfiles_sizes=[]
def get_file_from_medialist(size,filenamepatern=None,mode='IPhone',infolder=""):
    global _allfiles_names,_allfiles_sizes
    found=None
    ln=_allfiles_names
    sz=_allfiles_sizes
    if filenamepatern is not None:
        flistnames=fnmatch.filter(_allfiles_names,filenamepatern)
        if len(flistnames)==1:
            return flistnames[0]
        flistsizes = []
        for i in range(len(flistnames)):
            statinfo = os.stat(flistnames[i])
            fsize = statinfo.st_size
            fmoddate=statinfo.st_mtime
            flistsizes.append(fsize)

        try:
            indx=flistsizes.index(size)
            found=flistnames[ indx ]
        except:
            flistnames=_allfiles_sizes
    else:
        try:
            found=_allfiles_names[_allfiles_sizes.index(size) ]
        except:
            found=None
    if found is None and mode=='IPhone' and filenamepatern is not None:
        found=infolder+os.sep+'Library'+filenamepatern[1:-1]
        len(found)
    return found

def get_all_media_files(folder,filetypes):
    global _allfiles_names,_allfiles_sizes
    flistnames=[os.path.join(root,name)
                for root, dirs, files in os.walk(folder)
                for name in files
                if name.endswith(filetypes)]
    flistsizes = []
    for i in range(len(flistnames)):
        statinfo = os.stat(flistnames[i])
        fsize = statinfo.st_size
        #fmoddate=statinfo.st_mtime
        flistsizes.append(fsize)
    flist=[]
    if len(flistnames)>0:
        #flist = [flistnames, flistsizes]
        _allfiles_names=flistnames
        _allfiles_sizes=flistsizes

#end:get_all_media_files
################################################################################

def report_html(cs=None,msgs=None,infolder=None):
    global _allfiles_sizes,_allfiles_names
    if len(_allfiles_names)==0:
        if cs.mode=='Android':
            folder = infolder+os.sep+os.sep.join(['Media'])
        else:
            folder = infolder+os.sep+os.sep.join(['Library','Media'])
        if not os.path.exists(folder):
            print "{} folder not found".format(folder)
            sys.exit(1)
        get_all_media_files(folder,('.jpg','jpeg','.png','.tiff','mp3','.aac','.opus','.mp4','.mov'))

    lastdate= str(msgs[len(msgs)-1].msg_date).replace('-','')
    lastdate=lastdate.replace(' ','-')
    lastdate=lastdate.replace(':','')
    lastdate=lastdate[:-2]

    chats=""
    outfile=open("out.html","w")
    outfile.write('<!DOCTYPE html><html lang="en">')
    outfile.write('<head><link rel="stylesheet" href="out.css"></head>')
    outfile.write('<body>')
    #printing chat title
    #outfile.writable('<div class="chat-title">')
    #ctitle=
    #end:printing chat title

    outfile.write('<div class="container">')

    for idx,msg in enumerate(msgs):

        if msg.from_me:
            frm="ME"
        else:
            #frm=cs.contact_name
            frm=msg.contact_from.split('@')[0]

        #temp filtering by msg type
        #if  msg.msg_type!=0:
        #if  msg.parent_msg!=0:
        outfile.write(get_html_for_msg(frm,msg,infolder=infolder))

    outfile.write('</div">')
    outfile.write('</body></html>')
    outfile.close()

def get_html_for_msg(frm,msg,infolder=""):

    content=""
    date = str(msg.msg_date)[:10]
    if date != 'N/A' and date != 'N/A error':
        date = int(date.replace("-",""))


    if msg.msg_type==Message.CONTENT_IMAGE:
        #Search for offline file with current date (+2 days) and known media size
        #linkimage = findfile ("IMG", msg.media_size, msg.local_url, date, 2,mode=msg.mode,parent_folder=infolder)

        patern=None
        if msg.local_url !="":
            patern='*'+msg.local_url+'*'
        linkfile = get_file_from_medialist (size=msg.media_size,filenamepatern=patern,mode=msg.mode,infolder=infolder)
        #msg.media_url, msg.media_thumb,
        content+='<img src="{}" alt="Image" class="attachment"/><!-- {} -->'.format( linkfile,msg.media_thumb).encode('utf-8')

    elif msg.msg_type == Message.CONTENT_AUDIO:
        #linkaudio = findfile ("AUD", msg.media_size, msg.local_url, date, 2,mode=msg.mode,parent_folder=infolder)
        patern=None
        if msg.local_url !="":
            patern='*'+msg.local_url+'*'
        linkfile = get_file_from_medialist (size=msg.media_size,filenamepatern=patern,mode=msg.mode,infolder=infolder)
        content+='<audio controls><source src="{}" type="audio/ogg">Your browser does not support the audio element.</audio>'.format(linkfile).encode('utf-8')

    elif msg.msg_type==Message.CONTENT_VIDEO:
        #Search for offline file with current date (+2 days) and known media size
        #linkvideo = findfile ("VID", msg.media_size, msg.local_url, date, 2,mode=msg.mode,parent_folder=infolder)
        #msg.media_url, msg.media_thumb, linkvideo
        patern=None
        if msg.local_url !="":
            patern='*'+msg.local_url+'*'
        linkfile = get_file_from_medialist (size=msg.media_size,filenamepatern=patern,mode=msg.mode,infolder=infolder)
        content+='<video width="320" height="240" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>'.format(linkfile).encode('utf-8')

    elif msg.msg_type==Message.CONTENT_GIF_VIDEO:
        #Search for offline file with current date (+2 days) and known media size
        #linkvideo = findfile ("GIF", msg.media_size, msg.local_url, date, 2,mode=msg.mode,parent_folder=infolder)
        #msg.media_url, msg.media_thumb, linkvideo
        patern=None
        if msg.local_url !="":
            patern='*'+msg.local_url+'*'
        linkfile = get_file_from_medialist (size=msg.media_size,filenamepatern=patern,mode=msg.mode,infolder=infolder)
        content+='<video class="vid-attachment" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>'.format(linkfile).encode('utf-8')

    elif msg.msg_type==Message.CONTENT_MEDIA_THUMB:
        #linkmedia = findfile ("MEDIA_THUMB", y.media_size, y.local_url, date, 2)
        #msg.media_url, msg.media_thumb, linkmedia
        content+='<img src="{}" />'.format(msg.media_url).encode('utf-8')

    elif msg.msg_type==Message.CONTENT_MEDIA_NOTHUMB:
        tag='<a href="{}">Media</a>'
        #linkmedia = findfile ("MEDIA_NOTHUMB", y.media_size, y.local_url, date, 2)
        patern=None
        if msg.local_url !="":
            patern='*'+msg.local_url+'*'
        linkfile = get_file_from_medialist (size=msg.media_size,filenamepatern=patern,mode=msg.mode,infolder=infolder)
        if linkfile is None:
            linkfile="#"
        else:
            if linkfile.endswith(('.jpg','.jpeg','.tiff','.png')):
                tag='<img src="{}" alt="Image" class="attachment"/>'
            elif linkfile.endswith(('.mp3','.aac','.opus')):
                tag='<audio controls><source src="{}" type="audio/ogg">Your browser does not support the audio element.</audio>'
            elif linkfile.endswith(('.mp4','.mov')):
                tag='<video class="vid-attachment" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>'

        content+=tag.format(linkfile).encode('utf-8')

    elif msg.msg_type==Message.CONTENT_VCARD:
        if msg.vcard_name == "" or msg.vcard_name is None:
            vcardintro = ""
        else:
            vcardintro = "CONTACT: <b>" + msg.vcard_name + "</b><br>\n"
        msg.vcard_string = msg.vcard_string.replace ("\n", "<br>\n")
        content+="<p>{}</p>".format(vcardintro + msg.vcard_string).encode('utf-8')

    elif msg.msg_type==Message.CONTENT_GPS:
        try:
            if msg.gpsname == "" or msg.gpsname == None:
                msg.gpsname = ""
            else:
                msg.gpsname = "\n" + msg.gpsname
            msg.gpsname = msg.gpsname.replace ("\n", "<br>\n")
            if msg.media_thumb:
                content+='<p><a onclick="image(this.href);return(false);" target="image" href="https://maps.google.com/?q={},{}"><img src="{}" alt="GPS"/></a>{}</p>'.format(msg.latitude, msg.longitude, msg.media_thumb, msg.gpsname).encode('utf-8')
            else:
                content+='<p><a onclick="image(this.href);return(false);" target="image" href="https://maps.google.com/?q={},{}">GPS: {}, {}</a>{}</p>'.format(msg.latitude, msg.longitude, msg.latitude, msg.longitude, msg.gpsname).encode('utf-8')
        except:
            content+='<p>GPS N/A</p>'.encode('utf-8')

    elif msg.msg_type == Message.CONTENT_NEWGROUPNAME:
        msg.msg_type = Message.CONTENT_OTHER
    elif msg.msg_type != Message.CONTENT_TEXT:
        msg.msg_type = Message.CONTENT_OTHER
        # End of If-Clause, now text or other type of content:

    if msg.msg_type == Message.CONTENT_TEXT or msg.msg_type == Message.CONTENT_OTHER:
        #msgtext = convertsmileys ( y.msg_text )
        msgtext = re.sub(r'(http[^\s\n\r]+)', r'<a onclick="image(this.href);return(false);" target="image" href="\1">\1</a>', msg.msg_text)
        msgtext = re.sub(r'((?<!\S)www\.[^\s\n\r]+)', r'<a onclick="image(this.href);return(false);" target="image" href="http://\1">\1</a>', msgtext)
        msgtext = msgtext.replace ("\n", "<br>\n")
        try:
            #content+='<p>{}</p>'.format(msgtext).encode('utf-8')
            content+='<p>{}</p>'.format(msgtext)
        except:
            content+='<p>N/A</p>'.encode('utf-8')

    msg_templ="""
        <div class="message {_is_me}" id="{_id}">
            <div class="owner">{_frm}</div>
            <div class="content_date">{_d}</div>
            <div class="content">{_content}</div>
        </div>
    """
    is_sent=""
    if msg.from_me:
        is_sent=" sent-msg"

    return msg_templ.format(_is_me=is_sent,_id=msg.id,_frm=frm,_d=msg.msg_date,_content=content)
