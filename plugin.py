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
        QObject.connect(self.actionAddManhole, SIGNAL('triggered()'), self.addManhole )
        self.toolBar.addAction( self.actionAddManhole )
        
        #maptools
        self.mapToolAddManhole = QgsMapToolAddManhole( self.iface.mapCanvas() )
        
    def unload(self):
        del self.toolBar
        
    def toggleEditing(self,  enabled ):
        if enabled == True:
            
            #find the layer with name 'od_manhole'
            layerList = QgsMapLayerRegistry.instance().mapLayersByName( 'od_manhole' );
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
            
    def setTransactionToTools(self ):
        self.mapToolAddManhole.setTransaction( self.transaction )
        
    def addLayersToTransaction(self):
        manholeLayerList = QgsMapLayerRegistry.instance().mapLayersByName( 'od_manhole' );
        if len( manholeLayerList ) > 0:
            self.transaction.addLayer( manholeLayerList[0].id() )
        coverLayerList = QgsMapLayerRegistry.instance().mapLayersByName( 'od_cover' );
        if len( manholeLayerList ) > 0:
            self.transaction.addLayer( coverLayerList[0].id() )

    def addManhole(self):
        self.iface.mapCanvas().setMapTool( self.mapToolAddManhole )
