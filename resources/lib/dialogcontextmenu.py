
import xbmc, xbmcgui, xbmcaddon
import util
import dialogeditromcollection, dialogeditscraper, dialogdeleteromcollection, config
import nfowriter, wizardconfigxml
from nfowriter import *
from gamedatabase import *
from util import *
from config import *

ACTION_CANCEL_DIALOG = (9,10,51,92,110)
CONTROL_BUTTON_SETFAVORITE_GAME = 5118
CONTROL_BUTTON_SETFAVORITE_SELECTION = 5119

class ContextMenuDialog(xbmcgui.WindowXMLDialog):
		
	selectedGame = None
	gameRow = None
		
	def __init__(self, *args, **kwargs):
		# Don't put GUI sensitive stuff here (as the xml hasn't been read yet)
		Logutil.log('init ContextMenu', util.LOG_LEVEL_INFO)
		
		self.gui = kwargs[ "gui" ]
		
		self.doModal()
	
	def onInit(self):
		Logutil.log('onInit ContextMenu', util.LOG_LEVEL_INFO)
		
		pos = self.gui.getCurrentListPosition()
		if(pos != -1):
			self.selectedGame, self.gameRow = self.gui.getGameByPosition(self.gui.gdb, pos)
			
		#set mark favorite text
		if(self.gameRow != None):
			if(self.gameRow[util.GAME_isFavorite] == 1):
				buttonMarkFavorite = self.getControlById(CONTROL_BUTTON_SETFAVORITE_GAME)
				if(buttonMarkFavorite != None):
					buttonMarkFavorite.setLabel(util.localize(40033))
				buttonMarkFavorite = self.getControlById(CONTROL_BUTTON_SETFAVORITE_SELECTION)
				if(buttonMarkFavorite != None):
					buttonMarkFavorite.setLabel(util.localize(40034))
			
	
	def onAction(self, action):
		if (action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
	
	def onClick(self, controlID):
		if (controlID == 5101): # Close window button
			self.close()
		elif (controlID == 5110): # Import games
			self.close()
			self.gui.updateDB()
		elif (controlID == 5121): # Rescrape single games
			self.close()
			
			if(self.selectedGame == None or self.gameRow == None):
				xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(35013), util.localize(35014))
				return
			
			romCollectionId = self.gameRow[util.GAME_romCollectionId]
			romCollection = self.gui.config.romCollections[str(romCollectionId)]
			files = File(self.gui.gdb).getRomsByGameId(self.gameRow[util.ROW_ID])
			filename = files[0][0]
			romCollection.romPaths = (filename,)
						
			romCollections = {}
			romCollections[romCollection.id] = romCollection
			
			self.gui.rescrapeGames(romCollections)
			
		elif (controlID == 5122): # Rescrape selection
			self.close()
			
			romCollections = {}
			listSize = self.gui.getListSize()
			for i in range(0, listSize):
				selectedGame, gameRow = self.gui.getGameByPosition(self.gui.gdb, i)
				
				romCollectionId = gameRow[util.GAME_romCollectionId]
				
				try:
					romCollection = romCollections[str(romCollectionId)]
				except:				
					romCollection = self.gui.config.romCollections[str(romCollectionId)]
					romCollection.romPaths = []
					
				files = File(self.gui.gdb).getRomsByGameId(gameRow[util.ROW_ID])
				filename = files[0][0]
				romCollection.romPaths.append(filename)
				romCollections[romCollection.id] = romCollection
				
			self.gui.rescrapeGames(romCollections)
				
			
			#self.gui.updateDB()
		elif (controlID == 5111): # add Rom Collection			
			self.close()
			wizardconfigxml.ConfigXmlWizard().addRomCollection(self.gui.config)
			
			#update self.config
			statusOk, errorMsg = self.gui.config.readXml()
			if(statusOk == False):
				xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(35002), errorMsg)
				Logutil.log('Error reading config.xml: ' +errorMsg, util.LOG_LEVEL_INFO)
				return False, util.localize(35002) +' ' +errorMsg
			
			#import Games
			self.gui.updateDB()
			
		elif (controlID == 5112): # edit Rom Collection			
			self.close()
			constructorParam = "720p"
			editRCdialog = dialogeditromcollection.EditRomCollectionDialog("script-RCB-editromcollection.xml", util.getAddonInstallPath(), "Default", constructorParam, gui=self.gui)			
			del editRCdialog
			
			self.gui.config = Config()
			self.gui.config.readXml()
			
		elif (controlID == 5117): # edit scraper			
			self.close()			
			constructorParam = "720p"
			editscraperdialog = dialogeditscraper.EditOfflineScraper("script-RCB-editscraper.xml", util.getAddonInstallPath(), "Default", constructorParam, gui=self.gui)			
			del editscraperdialog
			
			self.gui.config = Config()
			self.gui.config.readXml()
		
		elif (controlID == 5113): #Edit Game Command			
			self.close()
			
			if(self.selectedGame == None or self.gameRow == None):
				xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(35015), util.localize(35014))
				return

			command = self.gameRow[util.GAME_gameCmd]
			
			keyboard = xbmc.Keyboard()
			keyboard.setHeading(util.localize(40035))
			if(command != None):
				keyboard.setDefault(command)
			keyboard.doModal()
			if (keyboard.isConfirmed()):
				command = keyboard.getText()
				Logutil.log("Updating game '%s' with command '%s'" %(str(self.gameRow[util.ROW_NAME]), command), util.LOG_LEVEL_INFO)
				Game(self.gui.gdb).update(('gameCmd',), (command,), self.gameRow[util.ROW_ID], True)
				self.gui.gdb.commit()
				
		elif (controlID == 5118): #(Un)Mark as Favorite
			self.close()
						
			if(self.selectedGame == None or self.gameRow == None):
				xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(35016), util.localize(35014))
				return
						
			isFavorite = 1
			if(self.gameRow[util.GAME_isFavorite] == 1):
				isFavorite = 0
			
			Logutil.log("Updating game '%s' set isFavorite = %s" %(str(self.gameRow[util.ROW_NAME]), str(isFavorite)), util.LOG_LEVEL_INFO)
			Game(self.gui.gdb).update(('isFavorite',), (isFavorite,), self.gameRow[util.ROW_ID], True)
			self.gui.gdb.commit()
						
			if(isFavorite == 0):
				isFavorite = ''
			self.selectedGame.setProperty('isfavorite', str(isFavorite))
			
		elif (controlID == 5119): #(Un)Mark as Favorite
			self.close()
						
			if(self.selectedGame == None or self.gameRow == None):
				xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(35016), util.localize(35014))
				return
						
			isFavorite = 1
			if(self.gameRow[util.GAME_isFavorite] == 1):
				isFavorite = 0
			
			listSize = self.gui.getListSize()
			for i in range(0, listSize):
				
				selectedGame, gameRow = self.gui.getGameByPosition(self.gui.gdb, i)
			
				Logutil.log("Updating game '%s' set isFavorite = %s" %(str(gameRow[util.ROW_NAME]), str(isFavorite)), util.LOG_LEVEL_INFO)
				Game(self.gui.gdb).update(('isFavorite',), (isFavorite,), gameRow[util.ROW_ID], True)
				selectedGame.setProperty('isfavorite', str(isFavorite))
			self.gui.gdb.commit()
			
		elif (controlID == 5120): #Export nfo files			
			self.close()
			nfowriter.NfoWriter().exportLibrary(self.gui)
			
		elif (controlID == 5114): #Delete Rom
			self.close()
			
			pos = self.gui.getCurrentListPosition()
			if(pos == -1):
				xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(35017), util.localize(35018))
				return					
			dialog = xbmcgui.Dialog()
			if dialog.yesno(util.localize(51010), util.localize(40036)):
				gameID = self.gui.getGameId(self.gui.gdb,pos)
				self.gui.deleteGame(gameID)
				self.gui.showGames()
				if(pos > 0):
					pos = pos - 1
					self.gui.setFilterSelection(self.gui.CONTROL_GAMES_GROUP_START, pos)
				else:
					self.gui.setFilterSelection(self.gui.CONTROL_GAMES_GROUP_START, 0)
		
		elif (controlID == 5115): #Remove Rom Collection			
			self.close()
						
			constructorParam = "720p"
			removeRCDialog = dialogdeleteromcollection.RemoveRCDialog("script-RCB-removeRC.xml", util.getAddonInstallPath(), "Default", constructorParam, gui=self.gui)			
			rDelStat = removeRCDialog.getDeleteStatus()
			if(rDelStat):
				selectedRCId = removeRCDialog.getSelectedRCId()
				rcDelStat = removeRCDialog.getRCDeleteStatus()
				self.gui.deleteRCGames(selectedRCId, rcDelStat, rDelStat)
				del removeRCDialog
				
		elif (controlID == 5116): #Clean DB
			self.close()
			self.gui.cleanDB()
				
		elif (controlID == 5223): #Open Settings
			self.close()			
			self.gui.Settings.openSettings()
	
	def onFocus(self, controlID):
		pass


	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except Exception, (exc):
			return None
		
		return control

