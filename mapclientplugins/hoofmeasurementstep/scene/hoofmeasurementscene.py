'''
Created on Jun 22, 2015

@author: hsorby
'''
from cmlibs.zinc.field import Field
from cmlibs.zinc.glyph import Glyph

from mapclientplugins.hoofmeasurementstep.scene.detection import DetectionScene
from mapclientplugins.hoofmeasurementstep.scene.marker import MarkerScene


class HoofMeasurementScene(object):
    '''
    classdocs
    '''

    def __init__(self, model):
        '''
        Constructor
        '''
        self._model = model
        self._detection_scene = DetectionScene(model.getDetectionModel())
        self._marker_scene = MarkerScene(model.getMarkerModel())
        self._setupVisualisation()

    def _setupVisualisation(self):
        coordinate_field = self._model.getCoordinateField()
        visibility_field = self._model.getVisibilityField()
        iso_scalar_field = self._model.getIsoScalarField()
        region = self._model.getRegion()
        scene = region.getScene()
        materialmodule = scene.getMaterialmodule()
        #         blue = materialmodule.findMaterialByName('blue')
        bone = materialmodule.findMaterialByName('bone')
        #         self._selection_graphics = self._createPointGraphics(scene, coordinate_field, yellow, None) # self._model.getSelectionGroupField())
        #         self._node_graphics = self._createPointGraphics(scene, coordinate_field, red, None) # self._model.getNodeGroupField())
        self._mesh_surface_graphics = self._createSurfaceGraphics(scene, coordinate_field, bone, visibility_field)
        self._mesh_contour_graphics = self._createContourGraphics(scene, coordinate_field, bone, iso_scalar_field)

    def _createSurfaceGraphics(self, scene, finite_element_field, material, subgroup_field):
        scene.beginChange()
        # Create a surface graphic and set it's coordinate field
        # to the finite element coordinate field.
        graphic = scene.createGraphicsSurfaces()
        graphic.setCoordinateField(finite_element_field)
        graphic.setMaterial(material)
        graphic.setSelectedMaterial(material)
        graphic.setSubgroupField(subgroup_field)
        scene.endChange()

        return graphic

    def _createContourGraphics(self, scene, finite_element_field, material, iso_scalar_field):
        scene.beginChange()
        # Create a surface graphic and set it's coordinate field
        # to the finite element coordinate field.
        graphic = scene.createGraphicsContours()
        graphic.setCoordinateField(finite_element_field)
        graphic.setMaterial(material)
        graphic.setSelectedMaterial(material)
        graphic.setIsoscalarField(iso_scalar_field)
        graphic.setListIsovalues(0.0)
        scene.endChange()

        return graphic

    def _createPointGraphics(self, scene, finite_element_field, material, subgroup_field):
        scene.beginChange()
        # Create a surface graphic and set it's coordinate field
        # to the finite element coordinate field.
        graphic = scene.createGraphicsPoints()
        graphic.setFieldDomainType(Field.DOMAIN_TYPE_NODES)
        graphic.setCoordinateField(finite_element_field)
        graphic.setMaterial(material)
        graphic.setSelectedMaterial(material)
        #         graphic.setSubgroupField(subgroup_field)
        attributes = graphic.getGraphicspointattributes()
        attributes.setGlyphShapeType(Glyph.SHAPE_TYPE_SPHERE)
        attributes.setBaseSize([1.0])
        #         surface = scene.createGraphicsSurfaces()
        #         surface.setCoordinateField(finite_element_field)
        scene.endChange()

        return graphic
