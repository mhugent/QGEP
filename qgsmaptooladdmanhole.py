from qgis.core import *
from qgis.gui import *
from PyQt4.QtGui import *

class QgsMapToolAddManhole( QgsMapToolEdit ):
    def __init__(self,  mapCanvas):
        QgsMapToolEdit.__init__( self,  mapCanvas )
        self.transaction = None
        
    def setTransaction(self,  transaction):
        self.transaction = transaction
        
    def canvasPressEvent(self,  e ):
        if self.transaction is None:
            return
        
        #get point
        point = self.toMapCoordinates( e.pos() ) #toLayerCoordinates( QgsMapLayer* layer, const QPoint& point );
        pointWkt = QgsGeometry.fromPoint( point ).exportToWkt()
        
        #execute function create_manhole
        errorMsg = ''
        sql = 'select qgep.create_manhole(ST_GeometryFromText(\'' + pointWkt +'\',21781));'
        memoryProvider = self.transaction.executeSql(  sql, errorMsg )
        if memoryProvider is None:
	    print errorMsg
            return
            
        pk = self.transactionStringReturnValue( memoryProvider )
        if pk is None:
	    print 'pk is none'
	    return
	    
	print pk
	    
	wastewaterStructureLayer = self.wastewaterStructureLayer()
	if wastewaterStructureLayer is None:
	    print 'wastewaterStructureLayer is None'
	    return
	    
	wastewaterStructure = self.firstFeatureForSubsetString( wastewaterStructureLayer, '"obj_id" = \'' + pk + '\'' )
	if wastewaterStructure is None:
	    print 'wastewaterStructure is None'
	    return
	    
	attributeDialog = QgsAttributeDialog( wastewaterStructureLayer, wastewaterStructure, False )
	if attributeDialog.dialog().exec_() == QDialog.Accepted:
	    featureAttributes = wastewaterStructure.attributes()
	    for i in range( len(featureAttributes) ):
		wastewaterStructureLayer.changeAttributeValue( wastewaterStructure.id(), i, featureAttributes[i] )
        
        self.canvas().refresh()
   
    def transactionStringReturnValue( self, memoryProvider ):
	iterator = memoryProvider.getFeatures( QgsFeatureRequest() )
	fet = QgsFeature()
        if not iterator.nextFeature( fet ):
            return None
        return fet.attributes()[0]
        
    def wastewaterStructureLayer( self ):
	wwStList = QgsMapLayerRegistry.instance().mapLayersByName( 'wastewater structure' )
	if len( wwStList ) < 1:
	    return None
	return wwStList[0]
	
    def firstFeatureForSubsetString( self, layer, subsetString ):
	bkString = layer.subsetString()
	layer.setSubsetString( subsetString )
	iterator = layer.getFeatures( QgsFeatureRequest() )
	feature = QgsFeature()
	if not iterator.nextFeature( feature ):
	    return None
	layer.setSubsetString( bkString )
	return feature
	
      
