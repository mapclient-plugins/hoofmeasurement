'''
Created on Jun 18, 2015

@author: hsorby
'''
from PySide import QtGui

from ui_hoofmeasurementwidget import Ui_HoofMeasurementWidget
from mapclientplugins.hoofmeasurementstep.scene.hoofmeasurementscene import HoofMeasurementScene

class HoofMeasurementWidget(QtGui.QWidget):
    '''
    classdocs
    '''


    def __init__(self, model, parent=None):
        '''
        Constructor
        '''
        super(HoofMeasurementWidget, self).__init__(parent)
        self._ui = Ui_HoofMeasurementWidget()
        self._ui.setupUi(self)
        
        self._callback = None
       
        self._model = model
        self._scene = HoofMeasurementScene(model)
        
        self._ui.widgetZinc.setContext(model.getContext())
        self._ui.widgetZinc.setModel(model.getMarkerModel())
#         self._ui.widgetZinc.setSelectionfilter(model.getSelectionfilter())
        
        self._makeConnections()
        
    def _makeConnections(self):
        self._ui.pushButtonDone.clicked.connect(self._doneExecution)
        self._ui.pushButtonViewAll.clicked.connect(self._viewAllButtonClicked)
        self._ui.horizontalSliderAngle.valueChanged.connect(self._angleSliderValueChanged)
        self._ui.widgetZinc.graphicsInitialized.connect(self._zincWidgetReady)
        self._ui.pushButtonDeleteNode.clicked.connect(self._ui.widgetZinc.deleteSelectedNodes)
        
    def getLandmarks(self):
        return self._model.getLandmarks()
        
    def setCoordinateDescription(self, coordinate_description):
        self._model.setCoordinateDescription(coordinate_description)
        
    def load(self, file_location):
        self._model.load(file_location)
        
    def registerDoneExecution(self, done_exectution):
        self._callback = done_exectution
        
    def _zincWidgetReady(self):
        self._ui.widgetZinc.setSelectionfilter(self._model.getSelectionfilter())
        
    def _viewAllButtonClicked(self):
        self._ui.widgetZinc.viewAll()
        
    def _doneExecution(self):
        self._callback()
        
    def _angleSliderValueChanged(self, value):
        angle = value - 50
        self._ui.labelAngle.setText(str(angle))
        self._model.setRotationAngle(angle)
        
        
        