'''
Created on Jun 22, 2015

@author: hsorby
'''
from cmlibs.utils.zinc.field import create_field_coordinates, create_field_iso_scalar_for_plane, create_field_plane_visibility
from cmlibs.utils.zinc.finiteelement import create_cube_element

from mapclientplugins.hoofmeasurementstep.model.plane import Plane


class DetectionModel(object):
    '''
    classdocs
    '''

    def __init__(self, parent, region):
        '''
        Constructor
        '''
        self._parent = parent
        self._region = region
        self._coordinate_field = create_field_coordinates(region.getFieldmodule(), managed=True)
        self._plane = self._setupDetectionPlane(region, self._coordinate_field)
        self._iso_scalar_field = create_field_iso_scalar_for_plane(region.getFieldmodule(), self._coordinate_field, self._plane)
        self._visibility_field = _createVisibilityField(region, self._coordinate_field, self._plane)
        self._extents = NameError

    def _setupDetectionPlane(self, region, coordinate_field):
        '''
        Adds a single finite element to the region and keeps a handle to the 
        fields created for the finite element in the following attributes(
        self-documenting names):
            '_coordinate_field'
            '_scale_field'
            '_scaled_coordinate_field'
            '_iso_scalar_field'
        '''
        fieldmodule = region.getFieldmodule()
        fieldmodule.beginChange()

        plane = Plane(fieldmodule)
        create_cube_element(fieldmodule.findMeshByDimension(3), coordinate_field,
                            [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 0], [0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 1, 1]])

        fieldmodule.endChange()

        return plane

    def getCoordinateField(self):
        return self._coordinate_field

    def getVisibilityField(self):
        return self._visibility_field

    def getRegion(self):
        return self._region

    def getIsoScalarField(self):
        return self._iso_scalar_field

    def getPlaneDescription(self):
        return self._plane.getNormal(), self._plane.getRotationPoint()

    def setExtents(self, extents):
        self._extents = extents
        node_coords = _convertExtentsToNodeCoords(extents)
        _adjustCube(self._region.getFieldmodule(), self._coordinate_field, node_coords)

    def setPlanePosition(self, normal, point):
        self._plane.setPlaneEquation(normal, point)

    def setPlaneNormal(self, normal):
        self._plane.setNormal(normal)


def _adjustCube(fieldmodule, coordinate_field, node_set):
    field_cache = fieldmodule.createFieldcache()

    nodeset = fieldmodule.findNodesetByName('nodes')
    for index, node_coordinate in enumerate(node_set):
        node_identifier = index + 1
        node = nodeset.findNodeByIdentifier(node_identifier)
        field_cache.setNode(node)
        coordinate_field.assignReal(field_cache, node_coordinate)


def _convertExtentsToNodeCoords(extents):
    x1, x2, y1, y2, z1, z2 = extents
    coords = [[x1, y1, z1], [x2, y1, z1], [x1, y2, z1], [x2, y2, z1],
              [x1, y1, z2], [x2, y1, z2], [x1, y2, z2], [x2, y2, z2]]

    return coords


def _createVisibilityField(region, coordinate_field, plane):
    fieldmodule = region.getFieldmodule()
    fieldmodule.beginChange()
    normal_field = plane.getNormalField()
    rotation_point_field = plane.getRotationPointField()
    visibility_field = create_field_plane_visibility(fieldmodule, coordinate_field, normal_field, rotation_point_field)
    fieldmodule.endChange()

    return visibility_field
