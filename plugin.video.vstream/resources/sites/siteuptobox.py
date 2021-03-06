#-*- coding: utf-8 -*-
#Vstream https://github.com/Kodi-vStream/venom-xbmc-addons
#johngf - V0.3
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui 
from resources.lib.handler.inputParameterHandler import cInputParameterHandler 
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler 
from resources.lib.parser import cParser 
from resources.lib.util import cUtil
from resources.lib.config import cConfig
import xbmc,xbmcgui,urllib,urllib2,re
from resources.lib.handler.premiumHandler import cPremiumHandler

SITE_IDENTIFIER = 'siteuptobox' 
SITE_NAME = '[COLOR dodgerblue]' + 'VotreCompteUptobox' + '[/COLOR]'
SITE_DESC = 'fichier sur compte uptobox'
 
BURL = 'https://uptobox.com/?op=my_files' 

def load(): 
    oGui = cGui()
    oPremiumHandler = cPremiumHandler('uptobox')
    
    if (cConfig().getSetting('hoster_uptobox_username') == '') and (cConfig().getSetting('hoster_uptobox_password') == ''):
        oGui.addText(SITE_IDENTIFIER, '[COLOR red]'+ 'Nécessite Un Compte Uptobox Premium ou Gratuit' + '[/COLOR]')
    else:
        if (oPremiumHandler.Readcookie('uptobox') != ''):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
            oGui.addDir(SITE_IDENTIFIER, 'showFile', 'MesFichiers', 'genres.png', oOutputParameterHandler)
    
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://Dossier/')
            oGui.addDir(SITE_IDENTIFIER, 'showFolder', 'MesDossiers', 'genres.png', oOutputParameterHandler)
        else:
            Connection = oPremiumHandler.Authentificate()
            if (Connection == False):
                xbmcgui.Dialog().notification('Info connexion', 'Connexion refusé', xbmcgui.NOTIFICATION_ERROR,2000,False)
                return
                
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://venom/')
            oGui.addDir(SITE_IDENTIFIER, 'showFile', 'MesFichiers', 'genres.png', oOutputParameterHandler)
    
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', 'http://Dossier/')
            oGui.addDir(SITE_IDENTIFIER, 'showFolder', 'MesDossiers', 'genres.png', oOutputParameterHandler)    
     

    oGui.setEndOfDirectory()
    
def showFile():
    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    
    oPremiumHandler = cPremiumHandler('uptobox')

    if 'uptobox.com' in sUrl:
        sHtmlContent = oPremiumHandler.GetHtml(sUrl)
    else:    
        sHtmlContent = oPremiumHandler.GetHtml(BURL)

    oParser = cParser()
    sPattern = '<td><a href="([^"]+)" class=".+?">([^<]+)<\/a><\/td><td>(.+?)<\/td>'
    aResult = oParser.parse(sHtmlContent, sPattern)  
    if (aResult[0] == True):
        total = len(aResult[1])
        dialog = cConfig().createDialog(SITE_NAME)
        for aEntry in aResult[1]:
            cConfig().updateDialog(dialog, total)
            if dialog.iscanceled():
                break

            sTitle = aEntry[1] + ' ' + '[' + aEntry[2] + ']'
            sHosterUrl = aEntry[0]
            
            sDisplayTitle = cUtil().DecoTitle(sTitle)
            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if (oHoster != False):
                oHoster.setDisplayName(sDisplayTitle)
                oHoster.setFileName(sTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl,'')
                
        cConfig().finishDialog(dialog)
        
    oGui.setEndOfDirectory()

def showFolder():
    oGui = cGui()
    oPremiumHandler = cPremiumHandler('uptobox')

    sHtmlContent = oPremiumHandler.GetHtml(BURL)
    
    oParser = cParser()
    sPattern = '<td class="tri">.+?<a href="([^"]+)" class="blue_link">(.+?)<\/a><\/td>'
    aResult = oParser.parse(sHtmlContent, sPattern)
    if (aResult[0] == True):
        total = len(aResult[1])
        dialog = cConfig().createDialog(SITE_NAME)
        for aEntry in aResult[1]:
            cConfig().updateDialog(dialog, total)
            if dialog.iscanceled():
                break

            sTitle = aEntry[1]
            sUrl = aEntry[0]
            if not sUrl.startswith('https'):
               sUrl = 'https://uptobox.com/' + sUrl
               
            sDisplayTitle = cUtil().DecoTitle(sTitle)  
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sUrl)
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oGui.addDir(SITE_IDENTIFIER, 'showFile', sDisplayTitle, 'genres.png', oOutputParameterHandler)
                
        cConfig().finishDialog(dialog)
        
    oGui.setEndOfDirectory()
       
def UploadFile():
    if (cConfig().getSetting('hoster_uptobox_username') == '') and (cConfig().getSetting('hoster_uptobox_password') == ''):
        return 
    oInputParameterHandler = cInputParameterHandler()
    sMediaUrl = oInputParameterHandler.getValue('sMediaUrl')
    # on récupère l'id
    sId = sMediaUrl.replace('https://uptobox.com/','')
    sId = sMediaUrl.replace('http://uptobox.com/','')
    #go page            
    Upurl = 'https://uptobox.com/?op=my_files&add_my_acc=' + sId

    oPremiumHandler = cPremiumHandler('uptobox')
    if (oPremiumHandler.Readcookie('uptobox') != ''):
        #xbmc.log('cookie trouvé')
        cookies = oPremiumHandler.Readcookie('uptobox')
        sHtmlContent = oPremiumHandler.GetHtmlwithcookies(Upurl,None,cookies)
        if (len(sHtmlContent) > 25):
            #xbmc.log('mais il a expiré')
            oPremiumHandler.Authentificate()
            cookies = oPremiumHandler.Readcookie('uptobox')
            sHtmlContent = oPremiumHandler.GetHtmlwithcookies(Upurl,None,cookies)
            #xbmc.log('nouveau cookie')
    else:
        #xbmc.log('aucun cookie')
        sHtmlContent = oPremiumHandler.GetHtml(Upurl)
        
    xbmc.executebuiltin("Dialog.Close(all,true)") 
    if ('dded to your account' in sHtmlContent):
         xbmcgui.Dialog().notification('Info upload','Fichier ajouté à votre compte',xbmcgui.NOTIFICATION_INFO,2000,False)      
    elif ('nvalid file' in sHtmlContent):
         xbmcgui.Dialog().notification('Info upload','Fichier introuvable',xbmcgui.NOTIFICATION_INFO,2000,False)
    else:
         xbmcgui.Dialog().notification('Info upload','Erreur',xbmcgui.NOTIFICATION_ERROR,2000,False) 
