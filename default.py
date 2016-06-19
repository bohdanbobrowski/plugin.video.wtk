# -*- coding: utf-8 -*-
import hashlib
import json
import os
import re
import time
import urllib
import urllib2
import xbmcaddon
import xbmcgui
import xbmcplugin
from operator import itemgetter

# TVP Historia - plugin do XBMC
# by Bohdan Bobrowski 2016

addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
linki = {}  

def getContents(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        html=response.read()
        response.close()        
        return html
    
def ListaKategorii():
        addLink('LIVE','http://wtk.live-ext.e55-po.insyscd.net/wtk.smil/playlist.m3u8','http://wtkplay.files.rd.insyscd.net/wtkplay-logo-player.jpg')
        html=getContents('http://www.wtk.pl/')
        categories=re.findall('<a href="(category[^"]+)">[\s]*<span class="not_selected">([^<]+)</span>[\s]*</a>',html)
        categories=sorted(categories, key=itemgetter(1))
        categories_thumbs = {}
        if os.path.isfile(addonUserDataFolder + "/categories_thumbs.json"):
            with open(addonUserDataFolder + "/categories_thumbs.json", "r") as f:
                for line in f:
                    categories_thumbs.update(json.loads(line))        
        for url,title in categories:
            title=title.strip()
            href="http://www.wtk.pl/"+url
            cache_key=url+time.strftime("%Y%m%d")
            if categories_thumbs.get(cache_key):
                image=categories_thumbs[cache_key]
            else:
                cat_html=getContents(href)
                images=re.findall('src="([^"]+)" class="video_medium_graphic"',cat_html)
                if len(images)>0:
                    image='http://www.wtk.pl/'+images[0]
                    categories_thumbs[cache_key]=image
                else:
                    image='http://www.wtk.pl/graphic/header/wtkplay_logo.png'
            addDir(title,href,image,1)
        categories_thumbs_json = json.dumps(categories_thumbs)
        categories_thumbs_file = open(addonUserDataFolder + "/categories_thumbs.json", "w")
        categories_thumbs_file.write(categories_thumbs_json)
        categories_thumbs_file.close()        

def ListaFilmow(url,name,page):
        html=getContents(url)
        filmy = re.findall('href="([^"]+)">[\s]*<div class="video_medium">[\s]*<img src="([^"]+)" class="video_medium_graphic" alt="([^"]+)',html)
        videos = {}
        if os.path.isfile(addonUserDataFolder + "/videos.json"):
            with open(addonUserDataFolder + "/videos.json", "r") as f:
                for line in f:
                    videos.update(json.loads(line))            
        for url,image,title in filmy:
            image='http://www.wtk.pl/'+image
            url='http://www.wtk.pl/'+url
            if videos.get(url) is not None:
                if videos[url]:
                    plikwideo=videos[url]
                    addLink(title, plikwideo, image) 
            else:
                html_video=getContents(url)
                url_iframe=re.findall('&amp;id=([0-9]+)&amp;',html_video)
                if url_iframe and url_iframe[0]:
                    url_iframe = url_iframe[0]                    
                    html_iframe=getContents('http://play.wtk.insys.pl/video/'+url_iframe)
                    plikwideo=re.findall('"(http\:\/\/wtkplay[a-zA-Z0-9\.\/\-_]+\.mp4)"',html_iframe)
                    print plikwideo
                    if plikwideo and plikwideo[0]:
                        plikwideo =  plikwideo[0]
                        videos[url] = plikwideo
                        addLink(title, plikwideo, image) 
        videos_json = json.dumps(videos)
        videos_file = open(addonUserDataFolder + "/videos.json", "w")
        videos_file.write(videos_json)
        videos_file.close()        

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
        return param

def addLink(name,url,iconimage):
        ok = True
        print name, url, iconimage
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addPageLink(name,url,page):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+'&page='+str(page)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
        liz.setInfo( type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addDir(name,url,iconimage,page):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+'&page='+str(page)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
              
params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        page=int(params["page"])
except:
        pass

if url==None or len(url)<1:
        ListaKategorii()
       
else:
        ListaFilmow(url,name,page)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
