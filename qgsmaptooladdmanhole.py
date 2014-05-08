from qgis.core import *
from qgis.gui import *

class QgsMapToolAddManhole( QgsMapToolEdit ):
    def __init__(self,  mapCanvas):
        QgsMapToolEdit.__init__( self,  mapCanvas )
        self.transaction = None
        
    def setTransaction(self,  transaction):
        self.transaction = transaction
        
    def canvasPressEvent(self,  e ):
        if self.transaction is None:
            return
            
        point = self.toMapCoordinates( e.pos() ) #toLayerCoordinates( QgsMapLayer* layer, const QPoint& point );
        pointWkt = QgsGeometry.fromPoint( point ).exportToWkt()
        sql = 'select qgep.create_manhole(ST_GeometryFromText(\'' + pointWkt +'\',21781));';
        print pointWkt
        print sql
        
        errorMsg = ''
        if not self.transaction.executeSql(  sql, errorMsg ):
            print errorMsg
        else:
            print 'ok'
        
        self.canvas().refresh()
