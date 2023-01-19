'''
Created on Jun 18, 2015

@author: hsorby
'''
from PySide6 import QtGui, QtWidgets

from mapclientplugins.hoofmeasurementstep.view.ui_hoofmeasurementwidget import Ui_HoofMeasurementWidget
from mapclientplugins.hoofmeasurementstep.scene.hoofmeasurementscene import HoofMeasurementScene

ANGLE_RANGE = 50


class HoofMeasurementWidget(QtWidgets.QWidget):
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

        angle_initial_value = 0
        slider_range = [0, 2 * ANGLE_RANGE]
        slider_initial_value = ANGLE_RANGE
        self._ui.lineEditAngle.setText(str(angle_initial_value))
        self._ui.horizontalSliderAngle.setValue(slider_initial_value)
        self._ui.horizontalSliderAngle.setMinimum(slider_range[0])
        self._ui.horizontalSliderAngle.setMaximum(slider_range[1])

        v = QtGui.QIntValidator(-ANGLE_RANGE, ANGLE_RANGE)
        self._ui.lineEditAngle.setValidator(v)
        self._ui.labelAngle.setText('Angle [{0}, {1}] (Degrees):'.format(-ANGLE_RANGE, ANGLE_RANGE))

        self._callback = None

        self._model = model
        self._scene = HoofMeasurementScene(model)

        self._ui.widgetZinc.setContext(model.getContext())
        self._ui.widgetZinc.setModel(model.getMarkerModel())
        self._ui.widgetZinc.setPlaneAngle(angle_initial_value)
        #         self._ui.widgetZinc.setSelectionfilter(model.getSelectionfilter())

        self._makeConnections()

    def _makeConnections(self):
        self._ui.pushButtonContinue.clicked.connect(self._continueExecution)
        self._ui.pushButtonViewAll.clicked.connect(self._viewAllButtonClicked)
        self._ui.horizontalSliderAngle.valueChanged.connect(self._angleSliderValueChanged)
        self._ui.widgetZinc.graphicsInitialized.connect(self._zincWidgetReady)
        self._ui.pushButtonDeleteNode.clicked.connect(self._ui.widgetZinc.deleteSelectedNodes)
        self._ui.lineEditAngle.returnPressed.connect(self._angleLineEditTextEditFinished)

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

    def _continueExecution(self):
        self._callback()

    def _angleSliderValueChanged(self, value):
        angle = value - 50
        self._ui.lineEditAngle.setText(str(angle))
        self._model.setRotationAngle(angle)
        self._ui.widgetZinc.setPlaneAngle(angle)

    def _angleLineEditTextEditFinished(self):
        angle = int(self._ui.lineEditAngle.text())
        self._ui.horizontalSliderAngle.setValue(angle + ANGLE_RANGE)
        self._model.setRotationAngle(angle)
        self._ui.widgetZinc.setPlaneAngle(angle)
