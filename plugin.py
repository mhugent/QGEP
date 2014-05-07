class QgepPlugin:
    def __init__(self,  iface ):
        self.iface = iface
        
    def initGui(self):
        #add qgep editing toolbar
        self.toolBar = self.iface.addToolBar( 'QGEP edit' )
        
    def unload(self):
        del self.toolBar
        pass
    
