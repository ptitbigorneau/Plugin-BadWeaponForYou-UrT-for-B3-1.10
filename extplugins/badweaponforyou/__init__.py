# -*- coding: utf-8 -*-
#
# BadWeaponForYou for UrbanTerror plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 PtitBigorneau - www.ptitbigorneau.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.6'

import b3, threading, thread, re
import b3.events
import b3.plugin
from b3.functions import getCmd

class BadweaponforyouPlugin(b3.plugin.Plugin):

    _adminPlugin = None
    _listplayersgear = {}
    _protectlevel = 20
    _saysgear = {
        'F':'Beretta 92G',
        'f':'Glock 18',
        'G':'Desert Eagle',
        'H':'SPAS-12',
        'I':'MP5K',
        'J':'UMP45',
        'K':'HK69',
        'L':'LR300ML',
        'M':'G36',
        'N':'PSG-1',
        'Z':'SR-8',
        'a':'AK-103',
        'c':'Negev',
        'e':'M4A1',
        'O':'HE Grenade',
        'P':'Flash Grenade',
        'Q':'HE Smoke',
        'R':'Kevlar Vest',
        'W':'Kevlar Helmet',
        'U':'Silencer',
        'V':'Laser Sight',
        'T':'MedKit',
        'S':'TacGoggles',
        'X':'Extra Anno',
        'g':'Colt1911',
        'h':'Ingram Mac11',
        'i':'FR-F1',
        'j':'Benelli M4 Super 90',
        'k':'FN Herstal P90',
        'l':'.44 Magnum',
        'A':''
    }

    _lgear = {    
        "none":["A", "None"],
        "beretta":["F", "Beretta 92G"],
        "de":["G", "Desert Eagle"],
        "glock":["f", "Glock 18"],
        "spas":["H", "SPAS-12"],
        "mp5":["I", "MP5K"],
        "ump":["J", "UMP45"],               
        "hk":["K", "HK69"],
        "lr300":["L", "LR300ML"],               
        "g36":["M", "G36"],
        "psg1":["N", "PSG-1"],
        "sr8":["Z", "SR-8"],
        "ak":["a", "AK-103"],
        "negev":["c", "Negev"],
        "m4":["e", "M4A1"],
        "he":["O", "HE Grenade"],
        "flash":["P", "Flash Grenade"],
        "smoke":["Q", "HE Smoke"],
        "kevlar":["R", "Kevlar Vest"],
        "helmet":["W", "Kevlar Helmet"],
        "silencer":["U", "Silencer"],
        "laser":["V", "Laser Sight"],
        "medkit":["T", "MedKit"],
        "tac":["S", "TacGoggles"],
        "xtra":["X", "Extra Ammo"],
        "colt":["g", "Colt1911"],
        "mac11":["h", "Ingram Mac11"],
        "frf1":["i", "FR-F1"],
        "benelli":["j", "Benelli M4 Super 90"],
        "fnp90":["k", "FN Herstal P90"],
        "magnum":["l", ".44 Magnum"]
    }
    
    _gears = ('beretta', 'de', 'glock', 'colt', 'mac11', 'spas', 'mp5', 'ump', 'hk', 'lr300', 'g36', 'psg1', 'sr8', 'ak', 'negev', 'm4', 'he', 'flash', 'smoke', 'kevlar', 'helmet', 'silencer', 'laser', 'medkit', 'tac', 'xtra', 'frf1', 'magnum', 'fnp90', 'benelli') 

    def onLoadConfig(self):

        self._protectlevel = self.getSetting('settings', 'protectlevel', b3.LEVEL, self._protectlevel)

    def onStartup(self):

        self._adminPlugin = self.console.getPlugin('admin')
        
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False
        
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = getCmd(self, cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)

        self.registerEvent('EVT_GAME_MAP_CHANGE', self.onGameMapChange)    

        self.registerEvent('EVT_CLIENT_GEAR_CHANGE', self.onClientChange)
        self.registerEvent('EVT_CLIENT_NAME_CHANGE', self.onClientChange)
        self.registerEvent('EVT_CLIENT_TEAM_CHANGE', self.onClientChange)

        self.gamename = self.console.gameName

        if self.gamename == 'iourt41':

            self.gmessage = 'gear[beretta|de|spas|mp5|ump|hk|lr300|g36|psg1|sr8|ak|negev|he|smoke|kevlar|helmet|silencer|laser|medkit|tag|xtra]'

        if self.gamename == 'iourt42':

            self.gmessage = 'gear[beretta|de|glock|colt|spas|mp5|ump|mac11|hk|lr300|g36|psg1|sr8|ak|negev|he|smoke|kevlar|helmet|silencer|laser|medkit|tag|xtra]'
        
        if self.gamename == 'iourt43':
        
            self.gmessage = 'gear[beretta|de|glock|colt|magnum|spas|benelli|mp5|ump|mac11|fnp90|hk|lr300|g36|psg1|sr8|frf1|ak|negev|he|smoke|kevlar|helmet|silencer|laser|medkit|tag|xtra]'

    def onGameMapChange(self,  event):       
            
        self._listplayersgear = {} 
    
    def onClientChange(self,  event):
    
        client = event.client
        fclient = client.id
        test = 0
        listgears = None
                
        if fclient in self._listplayersgear:
                    
            listbabclientgears = self._listplayersgear[fclient]
    
            for babclientgear in listbabclientgears:

                    if babclientgear in client.gear:
                        
                        test = test + 1
    
                        if test == 1:
                            listgears = self._saysgear[babclientgear]
                        else:
                            listgears = listgears + ", " + self._saysgear[babclientgear]
                            
        if test != 0:                                            
                            
            if client.team in (2, 3):
                self.console.write('forceteam %s %s' %(client.cid, 's'))
                client.message('^3Weapon /gear prohibited for %s ^3: ^7-%s-'%(client.exactName, listgears))
            
    def cmd_bwfy(self, data, client, cmd=None):
        """\
        <playername> <on or off> <gear> - prohibits or not a player from using an equipment
        """
        
        if data:
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
            client.message('!bwfy <playername> <on or off> <gear>')
            return
        
        sclient = self._adminPlugin.findClientPrompt(input[0], client)
        
        if not sclient:
            return False
        
        if sclient.maxLevel >= self._protectlevel:
            client.message('^3Invalid Command on %s!' %(sclient.exactName))
            return False
        
        if not input[1]:
            client.message('!bwfy <playername> <on or off> <gear>')
            return False
        nespace= input[1].count(' ')
        
        if nespace==0:
            client.message('!bwfy <playername> <on or off> <gear>')
            return False        
        
        tdata = input[1].split(' ')
        onoff = tdata[0]
        sgear = tdata[1]    
        
        if (onoff=="on") or (onoff=="off"):
            
            if onoff=='on':
                sayonoff='^2authorized'
            if onoff=='off':
                sayonoff='^1prohibited'
        else:
            client.message('!bwfy <playername> <on or off> <gear>')
            return False
        
        if sgear not in self._gears:
     
            client.message('!bwfy <playername> <on or off> <gear>')
            client.message('%s'%self.gmessage)
            return False
        
        if sclient:
        
            self._map=self.console.game.mapName
            
            rlgear = self._lgear[sgear]
            rgear = rlgear[0]
            ngear = rlgear[1]     
               
            sid=sclient.id
                            
            if onoff=="off":

                if rgear in sclient.gear:

                    self.console.write('forceteam %s %s' %(sclient.cid, 's'))
                
                    sclient.message('^3%s %s %s'%(sclient.exactName, ngear, sayonoff))
                   
                if sid in self._listplayersgear:
                
                    if rgear in self._listplayersgear[sid]:
                    
                        client.message('^3For %s ^7-%s-^3 is already %s'%(sclient.exactName, ngear , sayonoff))
                
                    else:
                    
                        self.console.say('^3For %s ^7-%s-^3 : %s'%(sclient.exactName, ngear, sayonoff))
                        self._listplayersgear[sid].append("%s"%rgear)

                else:

                    self._listplayersgear.update({sid:[rgear]})                
                                
            if onoff=="on":

                if sid in self._listplayersgear:
                
                    if rgear in self._listplayersgear[sid]:
    
                        self._listplayersgear[sid].remove(rgear)
                        sclient.message('^3Now %s: %s ^3again'%(ngear, sayonoff))
                        client.message('^3%s %s %s'%(sclient.exactName, ngear, sayonoff))
                        
                    else:

                        client.message('^3For %s %s ^3was not ^1prohibited'%(sclient.exactName, ngear))
 

                    if len(self._listplayersgear[sid]) == 0:

                        del self._listplayersgear[sid]
 
                else:
                
                    client.message('^3%s ^2No Weapon or Gear ^1prohibited'%(sclient.exactName))
                                    
        else:
            return False

    def cmd_listgear(self, data, client, cmd=None):
        """\
        <playername> - list of weapons and equipments of the player
                """
        
        if data:
            input = self._adminPlugin.parseUserCmd(data)
        else:
            client.message('!listgear <playername>')
            return

        sclient = self._adminPlugin.findClientPrompt(input[0], client)

        if not sclient:
            return False
               
        if (sclient):
        
            a=0
            b=1
            
            for i in xrange(7):
                if self._saysgear[sclient.gear[a:b]]!='':
                    client.message('%s^3 weapon / gear : ^7-%s-' % (sclient.exactName, self._saysgear[sclient.gear[a:b]]))            
                a=a+1
                b=b+1
                
        else:
            return False
    
    def cmd_listbwfy(self, data, client, cmd=None):
        """\
        <playername or all> - list prohibited of weapons and equipments of player 
                """

        if data:
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
            client.message('!listbwfy <playername or all>')
            return
        
        if input[0]=="all":
            lclient="all"
        
        else:
            lclient = self._adminPlugin.findClientPrompt(input[0], client)                
        
        if not lclient:
            return False
               
        if (lclient):
        
            if lclient=="all":
                
                test = False
                
                for x in self._listplayersgear:
                    
                    scid= '@'+str(x)
                    sdclient = self._adminPlugin.findClientPrompt(scid, client)
                        
                    for gear in self._listplayersgear[x]:
                    
                        client.message('^3Weapon /gear prohibited for ^2%s ^3: ^7-%s-'%(sdclient.exactName, self._saysgear[gear]))
                    
                    test = True

                if test == False:
                
                    client.message('^3No Players in Weapon /gear prohibited list')
                    
            else:
        
                try:

                    for gear in self._listplayersgear[lclient.id]:
                        client.message('^3Weapon /gear prohibited for %s ^3: ^7-%s-'%(lclient.exactName, self._saysgear[gear]))
  
                except:
                
                    client.message('%s ^3is not in Weapon /gear prohibited list'%(lclient.exactName))                  
        
        else:
            return False
    
    def cmd_mylistbwfy(self, data, client, cmd=None):
        """\
        list of your weapons and equipments prohibited 
                """
        
        try:

            for gear in self._listplayersgear[client.id]:
                client.message('^3Weapon /gear prohibited for %s ^3: ^7-%s-'%(client.exactName, self._saysgear[gear]))
  
        except:
                
            client.message('%s ^3is not in Weapon /gear prohibited list'%(client.exactName))
        

    def cmd_whogear(self, data, client, cmd=None):
        """\
        <gear> - list of players who have the weapon or gear specify
                """
        
        if data:
            input = self._adminPlugin.parseUserCmd(data)
        
        else:
            client.message('!whogear <gear>')
            client.message('%s'%self.gmessage)
            return
        
        sgear = input[0]
        
        if not sgear in self._gears:
     
            client.message('!whogear <gear>')
            client.message('%s'%self.gmessage)
            return False
               
        if (sgear):
        
            thread.start_new_thread(self.dowhogear, (client, sgear, cmd))
        
        else:
            return False

    def dowhogear(self, client, sgear, cmd):

        rlgear = self._lgear[sgear]
        rgear = rlgear[0]
        ngear = rlgear[1]  

        names = []
        test = 0        

        for c in self.console.clients.getClientsByLevel():
        
            sclient = self._adminPlugin.findClientPrompt(c.name, client)
            
            if sclient.team==1:
                steam="^7Spectator"
            if sclient.team==2:
                steam="^1Red"
            if sclient.team==3:
                steam="^4Blue"

            if rgear in sclient.gear:
                client.message('%s ^7team : %s ^7has ^2%s'%(sclient.exactName, steam, ngear))
                test = 1

        if test == 0:
            
            client.message('no player with ^2%s'%(ngear))    

        return
