# -*- coding: utf-8 -*-

# Debug
Debug = False

# Imports
import sys, re, urllib
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

__addon__ = xbmcaddon.Addon(id='plugin.video.tivion')
__info__ = __addon__.getAddonInfo
__plugin__ = __info__('name')
__version__ = __info__('version')
__icon__ = __info__('icon')
__fanart__ = __info__('fanart')
__path__ = __info__('path')
__cachedir__ = __info__('profile')
__language__ = __addon__.getLocalizedString
__settings__ = __addon__.getSetting

class Main:
  def __init__(self):
    if ("action=play" in sys.argv[2]):
      self.play()
    elif ("action=list" in sys.argv[2]):
      self.list_channels()
    else:
      self.list_countries()

  def list_countries(self):
    if Debug: self.LOG('List countries.')
    countries_url = urllib.urlopen(self.get_url('countries.py')).read()
    countries_list = re.findall("(.+?) \= dom\(\'iso_3166\'\, \'(.+?)\'\)", countries_url)
    for country_key, name in countries_list:
      listitem = xbmcgui.ListItem(name)
      listitem.setInfo(type="video",
                       infoLabels={"title" : name})
      parameters = '%s?action=list&country_key=%s' % (sys.argv[0], country_key)
      xbmcplugin.addDirectoryItems(int(sys.argv[1]), [(parameters, listitem, True)])
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  # TODO: Add radio streams
  def list_tv_radio(self):
    channels_url = urllib.urlopen(self.get_url('channels.py'))
    radio_list = re.findall("[^#]\['.+?', co.%s, cons.RADIO, '(.+?)', '([http,mms].+?)'\]" % self.Arguments('country_key'), channels_url)
    if radio_list != None:
      self.list_channels()
    else:
      pass

  def list_channels(self):
    if Debug: self.LOG('List channels.')
    channels_url = urllib.urlopen(self.get_url('channels.py')).read()
    channels_list = re.findall("[^#]\['.+?', co.%s, cons.TV, '(.+?)', '([http,mms].+?)'\]" % self.Arguments('country_key'), channels_url)
    for channelname, channelurl in channels_list:
      listitem = xbmcgui.ListItem(channelname, iconImage='DefaultVideo.png')
      listitem.setInfo(type="video",
                       infoLabels={"title" : channelname})
      parameters = '%s?action=play&url=%s&name=%s' % (sys.argv[0], urllib.quote_plus(channelurl), channelname)
      xbmcplugin.addDirectoryItems(int(sys.argv[1]), [(parameters, listitem, False)], len(channelname))
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.endOfDirectory(int(sys.argv[1]), True)

  def get_url(self, file):
    if Debug: self.LOG('Get %s URL' % file)
    try:
      url = urllib.urlopen('http://bazaar.launchpad.net/~shakaran/tivion/daily/view/head:/src/%s' % file).read()
    except IOError, e:
      if Debug: self.LOG('Error: could not connect to repository url. Check your connection or the repository URL.')
      return None
    url = re.findall("<a href=\"(.+?)\">download file</a>", url)
    if Debug:
      # http://bazaar.launchpad.net/~shakaran/tivion/tivion/download/head:/channels.py-20090902173635-8zjl0u0xzhky5rv1-2/channels.py
      self.LOG('%s URL: %s' % (file, 'http://bazaar.launchpad.net' + url[0]))
    if url != None:
      return 'http://bazaar.launchpad.net' + url[0]
    else:
      if Debug: self.LOG('Warning: could not get the channel url list repository. Check your connection or the repository URL.')
      return None

  def play(self):
    if Debug: self.LOG('Play stream.')
    title = unicode(xbmc.getInfoLabel("ListItem.Title"), "utf-8")
    listitem = xbmcgui.ListItem(title, iconImage=__icon__)
    # Play video...
    while xbmc.Player().play(self.Arguments('url'), listitem):
      time.sleep(10)
      print 'xbmc.isPlaying() = %s' % xbmc.isPlaying()
      if not xbmc.isPlaying():
        break

  def Arguments(self, arg):
    Arguments = dict(part.split('=') for part in sys.argv[2][1:].split('&'))
    return urllib.unquote_plus(Arguments[arg])

  def LOG(self, description):
    xbmc.log("[ADD-ON] '%s v%s': '%s'" % (__plugin__, __version__, description), xbmc.LOGNOTICE)

if (__name__ == '__main__'):
  Main()
