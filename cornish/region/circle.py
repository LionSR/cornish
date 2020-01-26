
import astropy
import astropy.units as u
from astropy.coordinates import SkyCoord

from math import radians as deg2rad
from math import degrees as rad2deg

import numpy as np
import starlink
import starlink.Ast as Ast

from .region import ASTRegion
from ..mapping import ASTMapping
from ..mapping import ASTFrame

__all__ = ["ASTCircle"]

CENTER_EDGE = 0
CENTER_RADIUS = 1

class ASTCircle(ASTRegion):
	'''
	ASTCircle is an ASTRegion that represents a circle.
	
	There are two accepted signatures for creating an ASTCircle:
	
	c = ASTCircle(frame, center, edge)
	c = ASTCircle(frame, center, radius)		
	'''
	def __init__(self, ast_circle=None, frame=None, center_point=None, edge_point=None, radius=None):
		'''
		Parameters
		----------
		centerPoint : numpy.ndarray, list, tuple
			Two elements that describe the center point of the circle in the provided frame in degrees
	
		edgePoint : numpy.ndarray, list, tuple
			Two elements that describe a point on the circumference of the circle in the provided frame in degrees
	
		radius : float
			The radius in degrees of the circle to be created.
		'''
		self._uncertainty = 4.848e-6 # defaults to 1 arcsec
		
		if ast_circle is not None:
			if isinstance(ast_circle, starlink.Ast.Circle):
				# make sure no other parameters are set
				if any([x is None for x in [frame, centerPoint, radius, edgePoint]]):
					raise Exception("ASTCircle: cannot specify both an ast_circle and any other parameter.")
				else:
					self.astObject = ast_circle
					return
			else:
				raise Exception("ASTCircle: The ast_circle provided was not of type starlink.Ast.Circle.")

		# check valid combination of parameters
		# -------------------------------------

		# make sure we have a frame we can work with
		if frame is None:
			raise Exception("ASTCircle: A frame must be specified when creating an ASTCircle.")
		else:
			if isinstance(frame, ASTFrame):
				self.frame = frame
			elif isinstance(frame, Ast.Frame):
				self.frame = ASTFrame(frame=frame)
			else:
				raise Exception("ASTCircle: unexpected frame type specified ('{0}').".format(type(frame)))
				
		if all([x is not None for x in [edge_point, radius]]):
			raise ValueError("Both 'edge_point' and 'radius' cannot be simultaneously specified.")
		if center_point is None:
			raise ValueError("The 'center_point' parameter must be set.")
		if all([x is None for x in [edge_point, radius]]):
			raise ValueError("Along with 'center_point', a 'radius' or 'edge_point' must be specified.")
		
		# input forms:
		#	CENTER_EDGE   (0) : circle specified by center point and any point on the circumference
		#	CENTER_RADIUS (1) : circle specified by  point and radius
		input_form = None
		if edge_point is None:
			input_form = CENTER_RADIUS
		
		# convert np.array types to lists so that the value can be used in 'any' and 'all' comparisons.
#		if isinstance(centerPoint, np.ndarray):
# 			centerPoint = centerPoint.tolist()
# 		if isinstance(edgePoint, np.ndarray):
# 			edgePoint = edgePoint.tolist()
# 		if isinstance(centerPoint, astropy.coordinates.SkyCoord):
# 			centerPoint = [centerPoint.ra.to(u.deg).value, centerPoint.dec.to(u.deg).value]
		
# 		if all([centerPoint, edgePoint]) or all([centerPoint, radius]):
# 			if edgePoint:
# 				input_form = CENTER_EDGE
# 			else:
# 				input_form = CENTER_RADIUS
# 		else:
# 			raise Exception("ASTCircle: Either 'centerPoint' and 'edgePoint' OR 'centerPoint' " + \
# 							"and 'radius' must be specified when creating an ASTCircle.")
		
		if isinstance(center_point, astropy.coordinates.SkyCoord):
			p1 = [center_point.ra.to(u.rad).value, center_point.dec.to(u.rad).value]
		elif isinstance(center_point[0], astropy.units.quantity.Quantity):
			try:
				p1 = [center_point[0].to(u.deg).value, center_point[1].to(u.deg).value]
			except astropy.units.core.UnitConversionError as e:
				# todo: be more descriptive
				raise e
		else:
			p1 = [deg2rad(center_point[0]), deg2rad(center_point[1])]
			
		if input_form == CENTER_EDGE:
			# p1 = center point, p2 = edge point
			if isinstance(edge_point, astropy.coordinates.SkyCoord):
				p2 = [edge_point.ra.to(u.rad).value, edge_point.dec.to(u.rad).value]
			else:
				p2 = [deg2rad(edge_point[0]), deg2rad(edge_point[1])]
		else:
			# p1 = center point, p2 = radius
			if isinstance(radius, astropy.units.quantity.Quantity):
				p2 = [radius.to(u.rad).value]
			else:
				p2 = [deg2rad(radius)]
		
		self.astObject = Ast.Circle( self.frame.astObject, input_form, p1, p2, unc=self.uncertainty)
	
	def __repr__(self):
		return "<{0}.{1} {2}: r={3}, center={4} deg>".format(self.__class__.__module__, self.__class__.__name__, hex(id(self)),
														self.radius, self.center)
	
	@property
	def radius(self):
		'''
		The radius of this circle region in degrees.
		
		@returns The radius as a geodesic distance in the associated coordinate system in degrees.
		'''
		center = None
		radius = None
		
		( center, radius, some_point_on_circumference ) = self.astObject.circlepars()
		
		return rad2deg(radius)
		
		# TODO: possibly cache this

	@property
	def center(self):
		'''
		The center of this circle region in degrees.
		
		Returns
		-------
		@returns A list of points [x,y] that describe the center of the circle in degrees.
		'''
		center = None
		radius = None
		
		( center, radius, some_point_on_circumference ) = self.astObject.circlepars()
		
		# TODO: possibly cache this
		
		return np.rad2deg(center)
			
	
