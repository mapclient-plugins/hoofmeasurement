"""
Created on Jun 18, 2015

@author: hsorby
"""
from math import cos, sin, pi

from cmlibs.zinc.context import Context
from cmlibs.utils.zinc.field import create_field_coordinates, create_field_iso_scalar_for_plane, create_field_plane_visibility
from cmlibs.utils.zinc.finiteelement import create_nodes, create_triangle_elements

from meshparser.vrmlparser.parser import VRMLParser

from mapclientplugins.hoofmeasurementstep.model.detection import DetectionModel
from mapclientplugins.hoofmeasurementstep.model.plane import Plane
from mapclientplugins.hoofmeasurementstep.utils.vectorops import sub, cross, normalize, matmult
from mapclientplugins.hoofmeasurementstep.model.marker import MarkerModel


class HoofMeasurementModel(object):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        self._coordinate_description = None
        self._file_location = None
        self._location = None
        self._context = Context("Hoof")
        self.defineStandardMaterials()
        self.defineStandardGlyphs()
        # First create coordinate field
        region = self._context.getDefaultRegion()
        field_module = region.getFieldmodule()
        self._coordinate_field = create_field_coordinates(field_module, managed=True)
        detection_region = self._context.getDefaultRegion().createChild('detection')
        self._detection_model = DetectionModel(self, detection_region)
        marker_region = self._context.getDefaultRegion().createChild('marker')
        self._marker_model = MarkerModel(self, marker_region)
        self._plane = self._setupDetectionPlane(region, self._coordinate_field)
        self._iso_scalar_field = create_field_iso_scalar_for_plane(field_module, self._coordinate_field, self._plane)
        self._visibility_field = _createVisibilityField(region, self._coordinate_field, self._plane)
        self._selection_filter = self._createSelectionFilter()

    def getDetectionModel(self):
        return self._detection_model

    def getMarkerModel(self):
        return self._marker_model

    def getSelectionfilter(self):
        return self._selection_filter

    def setCoordinateDescription(self, coordinate_description):
        point = coordinate_description[0]
        x = sub(coordinate_description[2], coordinate_description[0])
        y = sub(coordinate_description[1], coordinate_description[0])
        normal = normalize(cross(x, y))
        self._reference_normal = normal
        self._origin = point
        self._rotation_axis = normalize(y)
        self._detection_model.setPlanePosition(normal, point)
        self._plane.setPlaneEquation(normal, point)

    def setRotationAngle(self, angle):
        c = cos(angle * pi / 180.0)
        s = sin(angle * pi / 180.0)
        C = 1 - c
        x = self._rotation_axis[0]
        y = self._rotation_axis[1]
        z = self._rotation_axis[2]

        Q = [[x * x * C + c, x * y * C - z * c, x * z * C + y * s],
             [y * x * C + z * s, y * y * C + c, y * z * C - x * s],
             [z * x * C - y * s, z * y * C + x * s, z * z * C + c]]

        n = matmult(Q, self._reference_normal)

        self._plane.setNormal(n)
        self._detection_model.setPlaneNormal(n)

    def load(self, file_location):
        self._file_location = file_location
        v = VRMLParser()
        v.parse(file_location)
        self._nodes = v.getPoints()
        self._elements = _makeElementsOneBased(v.getElements())
        extents = _calculateExtents(self._nodes)
        self._detection_model.setExtents(extents)
        self._createMesh(self._nodes, self._elements)

    def setLocation(self, location):
        self._location = location

    def getPlaneDescription(self):
        return self._detection_model.getPlaneDescription()

    def getContext(self):
        return self._context

    def getCoordinateField(self):
        return self._coordinate_field

    def getRegion(self):
        return self._context.getDefaultRegion()

    def getVisibilityField(self):
        return self._visibility_field

    def getIsoScalarField(self):
        return self._iso_scalar_field

    def getLandmarks(self):
        return self._marker_model.getLandmarks()

    def _setupDetectionPlane(self, region, coordinate_field):
        """
        Adds a single finite element to the region and keeps a handle to the
        fields created for the finite element in the following attributes(
        self-documenting names):
            '_coordinate_field'
            '_scale_field'
            '_scaled_coordinate_field'
            '_iso_scalar_field'
        """
        fieldmodule = region.getFieldmodule()
        fieldmodule.beginChange()

        plane = Plane(fieldmodule)

        fieldmodule.endChange()

        return plane

    def _createMesh(self, nodes, elements):
        """
        Create a mesh from data extracted from a VRML file.
        The nodes are given as a list of coordinates and the elements
        are given as a list of indexes into the node list..
        """
        fieldmodule = self._coordinate_field.getFieldmodule()

        # First create all the required nodes
        create_nodes(self._coordinate_field, self._nodes)
        # then define elements using a list of node indexes
        mesh = fieldmodule.findMeshByDimension(2)
        create_triangle_elements(mesh, self._coordinate_field, self._elements)
        # Define all faces also
        fieldmodule.defineAllFaces()

    def _createSelectionFilter(self):
        m = self._context.getScenefiltermodule()
        r1 = m.createScenefilterRegion(self._detection_model.getRegion())
        r2 = m.createScenefilterRegion(self._marker_model.getRegion())
        o = m.createScenefilterOperatorOr()
        o.appendOperand(r1)
        o.appendOperand(r2)
        return o

    def defineStandardGlyphs(self):
        """
        Helper method to define the standard glyphs
        """
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()

    def defineStandardMaterials(self):
        """
        Helper method to define the standard materials.
        """
        material_module = self._context.getMaterialmodule()
        material_module.defineStandardMaterials()


def _makeElementsOneBased(elements_list):
    """
    Take a list of a list of element node indexes and increment the
    node index by one.
    """
    updated_elements = []
    for el in elements_list:
        updated_elements.append([n + 1 for n in el])

    return updated_elements


def _convertToElementList(elements_list):
    """
    Take a list of element node indexes deliminated by -1 and convert
    it into a list element node indexes list.
    """
    elements = []
    current_element = []
    for node_index in elements_list:
        if node_index == -1:
            elements.append(current_element)
            current_element = []
        else:
            # We also add one to the indexes to suit Zinc node indexing
            current_element.append(node_index + 1)

    return elements


def _calculateExtents(values):
    """
    Calculate the maximum and minimum for each coordinate x, y, and z
    Return the max's and min's as:
     [x_min, x_max, y_min, y_max, z_min, z_max]
    """
    x_min = 0
    x_max = 1
    y_min = 0
    y_max = 1
    z_min = 0
    z_max = 2
    if values:
        initial_value = values[0]
        x_min = x_max = initial_value[0]
        y_min = y_max = initial_value[1]
        z_min = z_max = initial_value[2]
        for coord in values:
            x_min = min([coord[0], x_min])
            x_max = max([coord[0], x_max])
            y_min = min([coord[1], y_min])
            y_max = max([coord[1], y_max])
            z_min = min([coord[2], z_min])
            z_max = max([coord[2], z_max])

    return [x_min, x_max, y_min, y_max, z_min, z_max]


def _createVisibilityField(region, coordinate_field, plane):
    fieldmodule = region.getFieldmodule()
    fieldmodule.beginChange()
    normal_field = plane.getNormalField()
    rotation_point_field = plane.getRotationPointField()
    visibility_field = create_field_plane_visibility(fieldmodule, coordinate_field, normal_field, rotation_point_field)
    fieldmodule.endChange()

    return visibility_field
