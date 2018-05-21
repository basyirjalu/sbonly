# -*- coding: utf-8 -*-
from Api import Poll, Talk, channel
from lib.curve.ttypes import *
import requests
import unicodedata,ntpath
import shutil
import json
from random import randint

def def_callback(str):
    print(str)

class LINE:

  mid = None
  authToken = None
  cert = None
  channel_access_token = None
  token = None
  obs_token = None
  refresh_token = None


  def __init__(self):
    self.Talk = Talk()
    self._session = requests.session()    

  def login(self, mail=None, passwd=None, cert=None, token=None, qr=False, callback=None):
    if callback is None:
      callback = def_callback
    resp = self.__validate(mail,passwd,cert,token,qr)
    if resp == 1:
      self.Talk.login(mail, passwd, callback=callback)
    elif resp == 2:
      self.Talk.login(mail,passwd,cert, callback=callback)
    elif resp == 3:
      self.Talk.TokenLogin(token)
    elif resp == 4:
      self.Talk.qrLogin(callback)
    else:
      raise Exception("invalid arguments")

    self.authToken = self.Talk.authToken
    self.cert = self.Talk.cert
    self._headers = {
              'X-Line-Application': 'DESKTOPWIN 11.2.5',
              'X-Line-Access': self.authToken, 
              'User-Agent': 'Line/8.0.0'
   }
    self.Poll = Poll(self.authToken)
    self.channel = channel.Channel(self.authToken)
    self.channel.login()	
    self.mid = self.channel.mid
    self.channel_access_token = self.channel.channel_access_token
    self.token = self.channel.token
    self.obs_token = self.channel.obs_token
    self.refresh_token = self.channel.refresh_token


  """User"""

  def getProfile(self):
    return self.Talk.client.getProfile()

  def getSettings(self):
    return self.Talk.client.getSettings()

  def getUserTicket(self):
    return self.Talk.client.getUserTicket()

  def updateProfile(self, profileObject):
    return self.Talk.client.updateProfile(0, profileObject)

  def updateSettings(self, settingObject):
    return self.Talk.client.updateSettings(0, settingObject)

  def cloneContactProfile(self, mid):
      contact = self.getContact(mid) 
      profile = self.getProfile()
      profile.displayName = contact.displayName
      profile.statusMessage = contact.statusMessage
      profile.pictureStatus = contact.pictureStatus
      self.updateDisplayPicture(profile.pictureStatus)
      return self.updateProfile(profile)
    
  def updateDisplayPicture(self, hash_id):
      return self.Talk.client.updateProfileAttribute(0, 8, hash_id)
  
  def cloneContactProfile(self, mid):
        contact = self.getContact(mid)
        profile = self.getProfile()
        profile.displayName = contact.displayName
        profile.statusMessage = contact.statusMessage
        profile.pictureStatus = contact.pictureStatus
        self.updateDisplayPicture(profile.pictureStatus)
        return self.updateProfile(profile)
        
  def cloneNameProfile(self, mid):
        contact = self.getContact(mid)
        profile = self.getProfile()
        profile.displayName = contact.displayName
        self.updateDisplayPicture(profile.pictureStatus)
        return self.updateProfile(profile)
        
  def cloneBioProfile(self, mid):
        contact = self.getContact(mid)
        profile = self.getProfile()
        profile.statusMessage = contact.statusMessage
        self.updateDisplayPicture(profile.pictureStatus)
        return self.updateProfile(profile)
        
  def clonePictureProfile(self, mid):
        contact = self.getContact(mid)
        profile = self.getProfile()
        profile.pictureStatus = contact.pictureStatus
        self.updateDisplayPicture(profile.pictureStatus)
        return self.updateProfile(profile) 
        
  def updateDisplayPicture(self, hash_id):
        return self.Talk.client.updateProfileAttribute(0, 8, hash_id)

  def updatebbbProfilePicture(self, path, type='p'):
        files = {'file': open(path, 'rb')}
        params = {'oid': self.profile.mid,'type': 'image'}
        if type == 'vp':
            params.update({'ver': '2.0', 'cat': 'vp.mp4'})
        data = {'params': self.genOBSParams(params)}
        r = self.server.postContent(self.server.LINE_OBS_DOMAIN + '/talk/p/upload.nhn', data=data, files=files)
        if r.status_code != 201:
            raise Exception('Update profile picture failure.')
        return True

  def updateProfilePicture(self, path):
    file=open(path, 'rb')
    files = {
        'file': file
    }
    params = {
        'name': 'media',
        'type': 'image',
        'oid': self.profile.mid,
        'ver': '1.0',
    }
    data={
        'params': json.dumps(params)
    }
    r = self.server.postContent(self.server.LINE_OBS_DOMAIN + '/talk/p/upload.nhn', data=data, files=files)
    if r.status_code != 201:
        raise Exception('Update profile picture failure.')
    return True

  def updateProfileVideoPicture(self, path):
        try:
            from ffmpy import FFmpeg
            files = {'file': open(path, 'rb')}
            data = {'params': self.genOBSParams({'oid': self.profile.mid,'ver': '2.0','type': 'video','cat': 'vp.mp4'})}
            r_vp = self.server.postContent(self.server.LINE_OBS_DOMAIN + '/talk/vp/upload.nhn', data=data, files=files)
            if r_vp.status_code != 201:
                raise Exception('Update profile video picture failure.')
            path_p = self.genTempFile('path')
            ff = FFmpeg(inputs={'%s' % path: None}, outputs={'%s' % path_p: ['-ss', '00:00:2', '-vframes', '1']})
            ff.run()
            self.updateProfilePicture(path_p, 'vp')
        except:
            raise Exception('You should install FFmpeg and ffmpy from pypi')

  def updateProfileCover(self, path, returnAs='bool'):
        if len(self.server.channelHeaders) < 1:
            raise Exception('LineChannel instance is required for acquire this action.')
        else:
            if returnAs not in ['objId','bool']:
                raise Exception('Invalid returnAs value')
            objId = self.uploadObjHome(path, type='image', returnAs='objId')
            home = self._channel.updateProfileCoverById(objId)
            if returnAs == 'objId':
                return objId
            elif returnAs == 'bool':
                return True

  """Operation"""

  def fetchOperation(self, revision, count):
        return self.Poll.client.fetchOperations(revision, count)

  def fetchOps(self, rev, count):
        return self.Poll.client.fetchOps(rev, count, 0, 0)

  def getLastOpRevision(self):
        return self.Talk.client.getLastOpRevision()

  def stream(self):
        return self.Poll.stream()

  """Message"""

  def kedapkedip(self, tomid, text):
        M = Message()
        M.to = tomid
        t1 = "\xf4\x80\xb0\x82\xf4\x80\xb0\x82\xf4\x80\xb0\x82\xf4\x80\xb0\x82"
        t2 = "\xf4\x80\x82\xb3\xf4\x8f\xbf\xbf"
        rst = t1 + text + t2
        M.text = rst.replace("\n", " ")
        return self.Talk.client.sendMessage(0, M)

  def sendMessage(self, messageObject):
        return self.Talk.client.sendMessage(0,messageObject)

  def sendText(self, Tomid, text):
        msg = Message()
        msg.to = Tomid
        msg.text = text

        return self.Talk.client.sendMessage(0, msg)
  
  def post_content(self, url, data=None, files=None):
        return self._session.post(url, headers=self._headers, data=data, files=files)

  def removeAllMessages(self, lastMessageId):
        return self.Talk.client.removeAllMessages(0,lastMessageId)        

  def like(self, mid, postid, likeType=1001):
    return self.channel.like(mid, postid, likeType)

  def sendImage(self, to_, path):
        M = Message(to=to_, text=None, contentType = 1)
        M.contentMetadata = None
        M.contentPreview = None
        M_id = self.Talk.client.sendMessage(0,M).id
        files = {
            'file': open(path, 'rb'),
        }
        params = {
            'name': 'media',
            'oid': M_id,
            'size': len(open(path, 'rb').read()),
            'type': 'image',
            'ver': '1.0',
        }
        data = {
            'params': json.dumps(params)            
        }       

        r = self.post_content('https://os.line.naver.jp/talk/m/upload.nhn', data=data, files=files)
        print r
        if r.status_code != 201:
            raise Exception('Upload image failure.')
        return True

  def sendImageWithURL(self, to_, url):
        """Send a image with given image url

        :param url: image url to send
        """
        path = 'pythonLine.data'

        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(path, 'w') as f:
                shutil.copyfileobj(r.raw, f)
        else:
            raise Exception('Download image failure.')

        try:
            self.sendImage(to_, path)
        except Exception as e:
            raise e

  def sendAudioWithURL(self, to_, url):
      path = 'pythonLiness.data'
      r = requests.get(url, stream=True)
      if r.status_code == 200:
         with open(path, 'w') as f:
            shutil.copyfileobj(r.raw, f)
      else:
         raise Exception('Download Audio failure.')
      try:
         self.sendAudio(to_, path)
      except Exception as e:
         raise e
  def sendAudio(self, to_, path):
      M = Message(to=to_,contentType = 3)
      M.contentMetadata = None
      M.contentPreview = None
      M_id = self.Talk.client.sendMessage(0,M).id
      files = {
         'file': open(path, 'rb'),
      }
      params = {
         'name': 'media',
         'oid': M_id,
         'size': len(open(path, 'rb').read()),
         'type': 'audio',
         'ver': '1.0',
      }
      data = {
         'params': json.dumps(params)
      }
      r = self.post_content('https://os.line.naver.jp/talk/m/upload.nhn', data=data, files=files)
      if r.status_code != 201:
         raise Exception('Upload image failure.')
      return True
  def sendVideo(self, to_, path):
      M = Message(to=to_,contentType = 2)
      M.contentMetadata = {
           'VIDLEN' : '0',
           'DURATION' : '0'
       }
      M.contentPreview = None
      M_id = self.Talk.client.sendMessage(0,M).id
      files = {
         'file': open(path, 'rb'),
      }
      params = {
         'name': 'media',
         'oid': M_id,
         'size': len(open(path, 'rb').read()),
         'type': 'video',
         'ver': '1.0',
      }
      data = {
         'params': json.dumps(params)
      }
      r = self.post_content('https://os.line.naver.jp/talk/m/upload.nhn', data=data, files=files)
      if r.status_code != 201:
         raise Exception('Upload image failure.')
      return True
  def sendVideoWithURL(self, to_, url):
      path = 'pythonLines.data'
      r = requests.get(url, stream=True)
      if r.status_code == 200:
         with open(path, 'w') as f:
            shutil.copyfileobj(r.raw, f)
      else:
         raise Exception('Download Audio failure.')
      try:
         self.sendVideo(to_, path)
      except Exception as e:
         raise e
  
  def sendMessageWithMention(self, to, text='', dataMid=[]):
      arr = []
      list_text=''
      if '[list]' in text.lower():
          i=0
          for l in dataMid:
              list_text+='\n@[list-'+str(i)+']'
              i=i+1
          text=text.replace('[list]', list_text)
      elif '[list-' in text.lower():
          text=text
      else:
          i=0
          for l in dataMid:
              list_text+=' @[list-'+str(i)+']'
              i=i+1
          text=text+list_text
      i=0
      for l in dataMid:
          mid=l
          name='@[list-'+str(i)+']'
          ln_text=text.replace('\n',' ')
          if ln_text.find(name):
              line_s=int( ln_text.index(name) )
              line_e=(int(line_s)+int( len(name) ))
          arrData={'S': str(line_s), 'E': str(line_e), 'M': mid}
          arr.append(arrData)
          i=i+1
      contentMetadata={'MENTION':str('{"MENTIONEES":' + json.dumps(arr).replace(' ','') + '}')}
      return self.sendMessage(to, text, contentMetadata)
     
  
  def sendGif(self, to_, path):
      M = Message(to=to_,contentType = 1)
      M.contentMetadata = {
           'VIDLEN' : '0',
           'DURATION' : '0'
       }
      M.contentPreview = None
      M_id = self.Talk.client.sendMessage(0,M).id
      files = {
         'file': open(path, 'rb'),
      }
      params = {
         'name': 'media',
         'oid': M_id,
         'size': len(open(path, 'rb').read()),
         'type': 'image',
         'ver': '1.0',
      }
      data = {
         'params': json.dumps(params)
      }
      r = self.post_content('https://os.line.naver.jp/talk/m/upload.nhn', data=data, files=files)
      if r.status_code != 201:
         raise Exception('Upload Gif failure.')
      return True
      
  def sendGifWithURL(self, to_, url):
      path = 'pythonLiness.data'
      r = requests.get(url, stream=True)
      if r.status_code == 200:
         with open(path, 'w') as f:
            shutil.copyfileobj(r.raw, f)
      else:
         raise Exception('Download Gif failure.')
      try:
         self.sendGif(to_, path)
      except Exception as e:
         raise e         

  def sendEvent(self, messageObject):
        return self.Talk.client.sendEvent(0, messageObject)

  def sendChatChecked(self, mid, lastMessageId):
        return self.Talk.client.sendChatChecked(0, mid, lastMessageId)

  def getMessageBoxCompactWrapUp(self, mid):
        return self.Talk.client.getMessageBoxCompactWrapUp(mid)

  def getMessageBoxCompactWrapUpList(self, start, messageBox):
        return self.Talk.client.getMessageBoxCompactWrapUpList(start, messageBox)

  def getRecentMessages(self, messageBox, count):
        return self.Talk.client.getRecentMessages(messageBox.id, count)

  def getMessageBox(self, channelId, messageboxId, lastMessagesCount):
        return self.Talk.client.getMessageBox(channelId, messageboxId, lastMessagesCount)

  def getMessageBoxList(self, channelId, lastMessagesCount):
        return self.Talk.client.getMessageBoxList(channelId, lastMessagesCount)

  def getMessageBoxListByStatus(self, channelId, lastMessagesCount, status):
        return self.Talk.client.getMessageBoxListByStatus(channelId, lastMessagesCount, status)

  def getMessageBoxWrapUp(self, mid):
        return self.Talk.client.getMessageBoxWrapUp(mid)

  def getMessageBoxWrapUpList(self, start, messageBoxCount):
        return self.Talk.client.getMessageBoxWrapUpList(start, messageBoxCount)
        
  def getCover(self,mid):
        h = self.getHome(mid)
        objId = h["result"]["homeInfo"]["objectId"]
        return "http://dl.profile.line-cdn.net/myhome/c/download.nhn?userid=" + mid+ "&oid=" + objId        

  """Contact"""


  def blockContact(self, mid):
        return self.Talk.client.blockContact(0, mid)


  def unblockContact(self, mid):
        return self.Talk.client.unblockContact(0, mid)


  def findAndAddContactsByMid(self, mid):
        return self.Talk.client.findAndAddContactsByMid(0, mid)


  def findAndAddContactsByMids(self, midlist):
        for i in midlist:
            self.Talk.client.findAndAddContactsByMid(0, i)

  def findAndAddContactsByUserid(self, userid):
        return self.Talk.client.findAndAddContactsByUserid(0, userid)

  def findContactsByUserid(self, userid):
        return self.Talk.client.findContactByUserid(userid)

  def findContactByTicket(self, ticketId):
        return self.Talk.client.findContactByUserTicket(ticketId)

  def getAllContactIds(self):
        return self.Talk.client.getAllContactIds()

  def getBlockedContactIds(self):
        return self.Talk.client.getBlockedContactIds()

  def getContact(self, mid):
        return self.Talk.client.getContact(mid)

  def getContacts(self, midlist):
        return self.Talk.client.getContacts(midlist)

  def getFavoriteMids(self):
        return self.Talk.client.getFavoriteMids()

  def getHiddenContactMids(self):
        return self.Talk.client.getHiddenContactMids()

  def CloneContactProfile(self, mid):
	contact = self.getContact(mid)
	profile = self.getProfile()
	profile.displayName = contact.displayName
	profile.statusMessage = contact.statusMessage
	profile.pictureStatus = contact.pictureStatus
	self.updateDisplayPicture(profile.pictureStatus)
	return self.updateProfile(profile)

  def updateDisplayPicture(self, hash_id):
        return self.Talk.client.updateProfileAttribute(0, 8, hash_id)


  """Group"""

  def findGroupByTicket(self, ticketId):
        return self.Talk.client.findGroupByTicket(ticketId)

  def acceptGroupInvitation(self, groupId):
        return self.Talk.client.acceptGroupInvitation(0, groupId)

  def acceptGroupInvitationByTicket(self, groupId, ticketId):
        return self.Talk.client.acceptGroupInvitationByTicket(0, groupId, ticketId)

  def cancelGroupInvitation(self, groupId, contactIds):
        return self.Talk.client.cancelGroupInvitation(0, groupId, contactIds)

  def createGroup(self, name, midlist):
        return self.Talk.client.createGroup(0, name, midlist)

  def getGroup(self, groupId):
        return self.Talk.client.getGroup(groupId)

  def getGroups(self, groupIds):
        return self.Talk.client.getGroups(groupIds)

  def getGroupIdsInvited(self):
        return self.Talk.client.getGroupIdsInvited()

  def getGroupIdsJoined(self):
        return self.Talk.client.getGroupIdsJoined()

  def inviteIntoGroup(self, groupId, midlist):
        return self.Talk.client.inviteIntoGroup(0, groupId, midlist)

  def kickoutFromGroup(self, groupId, midlist):
        return self.Talk.client.kickoutFromGroup(0, groupId, midlist)

  def leaveGroup(self, groupId):
        return self.Talk.client.leaveGroup(0, groupId)

  def rejectGroupInvitation(self, groupId):
        return self.Talk.client.rejectGroupInvitation(0, groupId)

  def reissueGroupTicket(self, groupId):
        return self.Talk.client.reissueGroupTicket(groupId)

  def updateGroup(self, groupObject):
        return self.Talk.client.updateGroup(0, groupObject)
        
  def findGroupByTicket(self,ticketId):
        return self.Talk.client.findGroupByTicket(0,ticketId)
        
  def downloadObjectMsg(self, messageId, returnAs='path', saveAs=''):
        if saveAs == '':
            saveAs = self.genTempFile('path')
        if returnAs not in ['path','bool','bin']:
            raise Exception('Invalid returnAs value')
        params = {'oid': messageId}
        url = self.server.urlEncode(self.server.LINE_OBS_DOMAIN, '/talk/m/download.nhn', params)
        r = self.server.getContent(url)
        if r.status_code == 200:
            self.saveFile(saveAs, r.raw)
            if returnAs == 'path':
                return saveAs
            elif returnAs == 'bool':
                return True
            elif returnAs == 'bin':
                return r.raw
        else:
            raise Exception('Download object failure.')

  def uploadObjTalk(self, path, type='image', returnAs='bool', objId=None, to=None):
        if returnAs not in ['objId','bool']:
            raise Exception('Invalid returnAs value')
        if type not in ['image','gif','video','audio','file']:
            raise Exception('Invalid type value')
        headers=None
        files = {'file': open(path, 'rb')}
        if type == 'image' or type == 'video' or type == 'audio' or type == 'file':
            e_p = self.server.LINE_OBS_DOMAIN + '/talk/m/upload.nhn'
            data = {'params': self.genOBSParams({'oid': objId,'size': len(open(path, 'rb').read()),'type': type})}
        elif type == 'gif':
            e_p = self.server.LINE_OBS_DOMAIN + '/r/talk/m/reqseq'
            files = None
            data = open(path, 'rb').read()
            params = {
                'oid': 'reqseq',
                'reqseq': '%s' % str(self.revision),
                'tomid': '%s' % str(to),
                'size': '%s' % str(len(data)),
                'range': len(data),
                'type': 'image'
            }
            headers = self.server.additionalHeaders(self.server.Headers, {
                'Content-Type': 'image/gif',
                'Content-Length': str(len(data)),
                'x-obs-params': self.genOBSParams(params,'b64')
            })
        r = self.server.postContent(e_p, data=data, headers=headers, files=files)
        if r.status_code != 201:
            raise Exception('Upload %s failure.' % type)
        if returnAs == 'objId':
            return objId
        elif returnAs == 'bool':
            return True

  def uploadObjHome(self, path, type='image', returnAs='bool', objId=None):
        if len(self.server.channelHeaders) < 1:
            raise Exception('LineChannel instance is required for acquire this action.')
        else:
            if returnAs not in ['objId','bool']:
                raise Exception('Invalid returnAs value')
            if type not in ['image','video','audio']:
                raise Exception('Invalid type value')
            if type == 'image':
                contentType = 'image/jpeg'
            elif type == 'video':
                contentType = 'video/mp4'
            elif type == 'audio':
                contentType = 'audio/mp3'
            if not objId:
                objId = int(time.time())
            file = open(path, 'rb').read()
            params = {
                'userid': '%s' % self.profile.mid,
                'oid': '%s' % str(objId),
                'range': len(file),
                'type': type
            }
            hr = self.server.additionalHeaders(self.server.channelHeaders, {
                'Content-Type': contentType,
                'Content-Length': str(len(file)),
                'x-obs-params': self.genOBSParams(params,'b64')
            })
            r = self.server.postContent(self.server.LINE_OBS_DOMAIN + '/myhome/c/upload.nhn', headers=hr, data=file)
            if r.status_code != 201:
                raise Exception('Upload object home failure.')
            if returnAs == 'objId':
                return objId
            elif returnAs == 'bool':
                return True

  def genTempFile(self, returnAs='path'):
        try:
            if returnAs not in ['file','path']:
                raise Exception('Invalid returnAs value')
            fName, fPath = 'linepy-%s-%i.bin' % (int(time.time()), randint(0, 9)), tempfile.gettempdir()
            if returnAs == 'file':
                return fName
            elif returnAs == 'path':
                return os.path.join(fPath, fName)
        except:
            raise Exception('tempfile is required')

  def genOBSParams(self, newList, returnAs='json'):
        oldList = {'name': self.genTempFile('file'),'ver': '1.0'}
        if returnAs not in ['json','b64','default']:
            raise Exception('Invalid parameter returnAs')
        oldList.update(newList)
        if 'range' in oldList:
            new_range='bytes 0-%s\/%s' % ( str(oldList['range']-1), str(oldList['range']) )
            oldList.update({'range': new_range})
        if returnAs == 'json':
            oldList=json.dumps(oldList)
            return oldList
        elif returnAs == 'b64':
            oldList=json.dumps(oldList)
            return base64.b64encode(oldList.encode('utf-8'))
        elif returnAs == 'default':
            return oldList
  
  def acquireGroupCallRoute(self, groupId):
        return self.Talk.client.call.acquireGroupCallRoute(groupId)

  def getGroupCall(self, ChatMid):
        return self.Talk.client.call.getGroupCall(ChatMid)

  def inviteIntoGroupCall(self, chatId, contactIds=[]):
        return self.Talk.client.call.inviteIntoGroupCall(chatId, contactIds)
  
  """Room"""

  def createRoom(self, midlist):
    return self.Talk.client.createRoom(0, midlist)

  def getRoom(self, roomId):
    return self.Talk.client.getRoom(roomId)

  def inviteIntoRoom(self, roomId, midlist):
    return self.Talk.client.inviteIntoRoom(0, roomId, midlist)

  def leaveRoom(self, roomId):
    return self.Talk.client.leaveRoom(0, roomId)

  """TIMELINE"""

  def new_post(self, text):
    return self.channel.new_post(text)

  def like(self, mid, postid, likeType=1001):
    return self.channel.like(mid, postid, likeType)

  def comment(self, mid, postid, text):
    return self.channel.comment(mid, postid, text)

  def activity(self, limit=20):
    return self.channel.activity(limit)

  def getAlbum(self, gid):

      return self.channel.getAlbum(gid)
  def changeAlbumName(self, gid, name, albumId):
      return self.channel.changeAlbumName(gid, name, albumId)

  def deleteAlbum(self, gid, albumId):
      return self.channel.deleteAlbum(gid,albumId)

  def getNote(self,gid, commentLimit, likeLimit):
      return self.channel.getNote(gid, commentLimit, likeLimit)

  def getDetail(self,mid):
      return self.channel.getDetail(mid)

  def getHome(self,mid):
      return self.channel.getHome(mid)

  def createAlbum(self, gid, name):
      return self.channel.createAlbum(gid,name)

  def createAlbum2(self, gid, name, path):
      return self.channel.createAlbum(gid, name, path, oid)

  """Personalize"""
    
  def cloneContactProfile(self, mid):
      contact = self.getContact(mid)
      profile = self.getProfile()
      profile.displayName = contact.displayName
      profile.statusMessage = contact.statusMessage
      profile.pictureStatus = contact.pictureStatus
      self.updateDisplayPicture(profile.pictureStatus)
      return self.updateProfile(profile)
  
  def updateDisplayPicture(self, hash_id):
      return self.Talk.client.updateProfileAttribute(0, 8, hash_id)

  def parseUrl(self, path):
        return self.LINE_HOST_DOMAIN + path

  def urlEncode(self, url, path, params=[]):
        try:        # Works with python 2.x
            return url + path + '?' + urllib.urlencode(params)
        except:     # Works with python 3.x
            return url + path + '?' + urllib.parse.urlencode(params)

  def getJson(self, url, allowHeader=False):
        if allowHeader is False:
            return json.loads(self._session.get(url).text)
        else:
            return json.loads(self._session.get(url, headers=self.Headers).text)

  def setChannelHeadersWithDict(self, headersDict):
        self.channelHeaders.update(headersDict)

  def setChannelHeaders(self, argument, value):
        self.channelHeaders[argument] = value

  def additionalHeaders(self, source, newSource):
        headerList={}
        headerList.update(source)
        headerList.update(newSource)
        return headerList

  def optionsContent(self, url, data=None, headers=None):
        if headers is None:
            headers=self.Headers
        return self._session.options(url, headers=headers, data=data)

  def postContent(self, url, data=None, files=None, headers=None):
        if headers is None:
            headers=self.Headers
        return self._session.post(url, headers=headers, data=data, files=files)

  def getContent(self, url, headers=None):
        if headers is None:
            headers=self.Headers
        return self._session.get(url, headers=headers, stream=True)

  def deleteContent(self, url, data=None, headers=None):
        if headers is None:
            headers=self.Headers
        return self._session.delete(url, headers=headers, data=data)
            
  def __validate(self, mail, passwd, cert, token, qr):
    if mail is not None and passwd is not None and cert is None:
      return 1
    elif mail is not None and passwd is not None and cert is not None:
      return 2
    elif token is not None:
      return 3
    elif qr is True:
      return 4
    else:
      return 5

  def loginResult(self, callback=None):
    if callback is None:
      callback = def_callback

      prof = self.getProfile()

      print("\n\n______________TEAM POTTERᴮᵒᵗ྄______________")
      print("\nUser mid : " + prof.mid)
      print("\n Names mu brade : " + prof.displayName)
      print("\nUser token : " + self.authToken)
      print("\n______________TEAM POTTERᴮᵒᵗ྄______________")
      print("Muachh " + self.cert if self.cert is not None else "")
