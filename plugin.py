from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgsmaptooladdmanhole import QgsMapToolAddManhole

class QgepPlugin:
    def __init__(self,  iface ):
        self.iface = iface
        
    def initGui(self):
        #add qgep editing toolbar
        self.toolBar = self.iface.addToolBar( 'QGEP edit' )
        
        #edit toggle action
        self.actionToggleEdit = QAction( 'Toggle editing',  None )
        self.actionToggleEdit.setCheckable( True )
        QObject.connect( self.actionToggleEdit,  SIGNAL('toggled( bool )'),  self.toggleEditing )
        self.toolBar.addAction( self.actionToggleEdit )
        
        #add manhole action
        self.actionAddManhole = QAction('Add manhole',  None )
        self.actionAddManhole.setCheckable( True )
        QObject.connect(self.actionAddManhole, SIGNAL('triggered()'), self.addManhole )
        self.toolBar.addAction( self.actionAddManhole )
        
        #maptools
        self.mapToolAddManhole = QgsMapToolAddManhole( self.iface.mapCanvas() )
        self.mapToolAddManhole.setAction( self.actionAddManhole )
        
        self.setActionsEnabled( False )
        
    def unload(self):
        del self.toolBar
        
    def toggleEditing(self,  enabled ):
        if enabled == True:
            
            #find the layer with name 'od_manhole'
            layerList = QgsMapLayerRegistry.instance().mapLayersByName( 'manhole' );
            if len( layerList ) < 1:
                QMessageBox.critical( None,  QApplication.translate( 'Error'),  QApplication.translate('Layer od_manhole not found') )
                self.transaction = None
                return
            
            connectionString = QgsDataSourceURI(layerList[0].source() ).connectionInfo()
            print connectionString
            self.transaction = QgsTransaction(  connectionString,  'postgres' )
            self.addLayersToTransaction()
            errorMsg = ''
            if not self.transaction.begin( errorMsg ):
                del self.transaction
                QMessageBox.critical( None,  QApplication.translate( 'Plugin','Error'),  QApplication.translate('plugin','Transaction failed') )
                self.transaction = None
            self.setTransactionToTools()
            self.setActionsEnabled( True )
            self.setTransactionLayersEditable( True )
        else:
            if self.transaction is None:
                return
                
            errorMsg = ''
            #todo: show dialog if commit / rollback
            if QMessageBox.question( None,  QApplication.translate('Plugin','Save changes'),  QApplication.translate(  'Plugin','Commit changes?' ),  QMessageBox.Yes,  QMessageBox.No  ) == QMessageBox.Yes:
                self.transaction.commit( errorMsg )
            else:
                self.transaction.rollback( errorMsg )
            del self.transaction
            self.transaction = None
            self.setTransactionToTools()
            self.setActionsEnabled( False )
            self.setTransactionLayersEditable( False )
            
	self.iface.mapCanvas().refresh()
	
    def setActionsEnabled( self, enabled ):
      self.actionAddManhole.setEnabled( enabled )
            
    def setTransactionToTools(self ):
        self.mapToolAddManhole.setTransaction( self.transaction )
        
    def addLayersToTransaction(self):
	self.addLayerToTransaction( 'manhole')
	self.addLayerToTransaction( 'cover' )
	self.addLayerToTransaction( 'structure part' )
	self.addLayerToTransaction( 'wastewater networkelement' )
	self.addLayerToTransaction( 'wastewater structure' )
	self.addLayerToTransaction( 'wastewater node' )
            
    def addLayerToTransaction( self, layerName ):
	layerList = QgsMapLayerRegistry.instance().mapLayersByName( layerName )
	if len(layerList) > 0:
	    self.transaction.addLayer( layerList[0].id() )
	    
    def setTransactionLayersEditable( self, editable ):
	#self.setLayerEditable( 'manhole', editable )
	#self.setLayerEditable( 'cover', editable )
	#self.setLayerEditable( 'structure part', editable )
	#self.setLayerEditable( 'wastewater networkelement', editable )
	self.setLayerEditable( 'wastewater structure', editable )
	#self.setLayerEditable( 'wastewater node', editable )
	
    def setLayerEditable( self, layername, editable ):
	layerList = QgsMapLayerRegistry.instance().mapLayersByName( layername )
	if len( layerList ) < 1:
	  return
	layer = layerList[0]
	if layer.type() == QgsMapLayer.VectorLayer:
	  if editable:
	    layer.startEditing()
	  else:
	    layer.rollBack()

    def addManhole(self):
        self.iface.mapCanvas().setMapTool( self.mapToolAddManhole )
