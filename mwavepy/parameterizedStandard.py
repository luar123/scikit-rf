
#       parametertizedStandard.py
#       
#       
#       Copyright 2010 alex arsenovic <arsenovic@virginia.edu>
#       
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later versionpy.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
'''
provides Parameterized Standard class.  
'''
import numpy as npy
from copy import copy

from discontinuities.variationalMethods import *

class ParameterizedStandard(object):
	'''
	A parameterized standard represents a calibration standard which 
	has uncertainty in its response. This uncertainty is functionally 
	known, and 	represented by a parametric function, where the 
	uknown quantity is the adjustable parameter. 
	
	'''
	def __init__(self, function=None, parameters={}, **kwargs):
		'''
		takes:
			function: a function which will be called to generate
				a Network type, to be used as a ideal response. 
			
			parameters: an dictionary holding an list of parameters,
				which will be the dependent variables to optimize.
				these are passed to the network creating function.
			 
			**kwargs: keyword arguments passed to the function, but 
				not used in parametric optimization.
		'''
		self.kwargs = kwargs
		self.parameters = parameters
		self.function = function

	
	@property
	def parameter_keys(self):
		'''
		returns a list of parameter dictionary keys in alphabetical order
		'''
		keys = self.parameters.keys()
		keys.sort()
		return keys

	@property	
	def parameter_array(self):
		'''
		This property provides a 1D-array interface to the parameters 
		dictionary. This is needed to intereface teh optimizing function
		because it only takes a 1D-array. Therefore, order must be 
		preserved with accessing and updating the parameters through this
		array. To handle this I make it return and update in alphebetical
		order of the parameters dictionary keys. 
		'''
		return npy.array([self.parameters[k] for  k in self.parameter_keys])

	@parameter_array.setter	
	def parameter_array(self,input_array):
		counter = 0
		for k in self.parameter_keys:
			self.parameters[k]= input_array[counter]
			counter+=1
	@property
	def number_of_parameters(self):
		'''
		the number of parameters this standard has
		'''
		return len(self.parameter_keys)
	
	@property
	def s(self):
		'''
		a direct access to the calulated networks' s-matrix
		'''
		return self.network.s

	@property
	def network(self):
		'''
		 a Networks instance generated by calling self.function(), for 
		the current set of parameters (and kwargs) 
		'''
		tmp_args = copy(self.kwargs)
		tmp_args.update(self.parameters)
		return self.function(**tmp_args)


## pre-defined parametrized standard classes

class PS_Parameterless(ParameterizedStandard):
	'''
		A parameterless standard. 
		this is needed so that the calibration algorithm doesnt have to
		handle more than one type of standard
		'''
	def __init__(self, ideal_network):
		'''
		takes:
			ideal_network: a Network instance of the standard
		'''
		ParameterizedStandard.__init__(self, \
			function  = lambda: ideal_network)
		
	
class PS_Match_TranslationMissalignment(ParameterizedStandard):
	'''
	A match with unknown translation missalignment.
	the initial guess for missalignment is [a/10,a/10], where a is the 
	waveguide width
	'''
	def __init__(self, wb, initial_offset= 1./10 , **kwargs):
		'''
		takes:
			wb: a WorkingBand type, with a RectangularWaveguide object
				for its tline property.
			initial_offset: initial offset guess, as a fraction of a, 
				(the waveguide width dimension)
			**kwargs: passed to self.function
		'''
		wg = wb.tline
		kwargs.update({'wg':wg,'freq':wb.frequency})
		
		ParameterizedStandard.__init__(self, \
			function = translation_offset,\
			parameters = {'delta_a':wg.a*initial_offset, \
				'delta_b':wg.a*initial_offset},\
			**kwargs\
			)

class PS_DelayedTermination_TranslationMissalignment(ParameterizedStandard):
	'''
	A known Delayed Termination with unknown translation missalignment.
	the initial guess for missalignment defaults to [1/10,1/10]*a,
	where a is the 	waveguide width
	'''
	def __init__(self, wb,d,Gamma0,initial_offset= 1./10, **kwargs):
		'''
		takes:
			wb: a WorkingBand type, with a RectangularWaveguide object
				for its tline property.
				d: distance to termination
				Gamma0: reflection coefficient off termination at termination
			initial_offset: initial offset guess, as a fraction of a, 
				(the waveguide width dimension)
			**kwargs: passed to self.function
		'''
		wg = wb.tline
		kwargs.update({'wg':wg,'freq':wb.frequency,'d':d,'Gamma0':Gamma0})
		
		ParameterizedStandard.__init__(self, \
			function = terminated_translation_offset,\
			parameters = {'delta_a':wg.a*initial_offset, \
						'delta_b':wg.a*initial_offset},\
			**kwargs\
			)

class PS_DelayedTermination_UnknownLength(ParameterizedStandard):
	'''
	A  Delayed Termination of unknown length, but known termination
	'''
	def __init__(self, wb,d,Gamma0,**kwargs):
		'''
		takes:
			wb: a WorkingBand type, with a RectangularWaveguide object
				for its tline property.
			d: distance to termination
			Gamma0: reflection coefficient off termination at termination
			**kwargs: passed to self.function
		'''
		wg = wb.tline
		kwargs.update({'wg':wg,'freq':wb.frequency,'Gamma0':Gamma0,\
			'delta_a':0, 'delta_b':0})
		
		ParameterizedStandard.__init__(self, \
			function = terminated_translation_offset,\
			parameters = {'d':d},\
			**kwargs\
			)
class PS_DelayedTermination_UnknownLength_UnknownTermination(ParameterizedStandard):
	'''
	A  Delayed Termination of unknown length or termination
	'''
	def __init__(self, wb,d,Gamma0,**kwargs):
		'''
		takes:
			wb: a WorkingBand type, with a RectangularWaveguide object
				for its tline property.
			d: distance to termination
			Gamma0: reflection coefficient off termination at termination
			**kwargs: passed to self.function
		'''
		
		ParameterizedStandard.__init__(self, \
			function = wb.delay_load,\
			parameters = {'d':d,'Gamma0':Gamma0},\
			**kwargs\
			)
class PS_DelayedTermination_UnknownLength_TranslationMissalignment(ParameterizedStandard):
	'''
	A known Delayed Termination with unknown translation missalignment.
	the initial guess for missalignment defaults to [1/10,1/10]*a,
	where a is the 	waveguide width
	'''
	def __init__(self, wb,d,Gamma0,initial_offset= 1./10, **kwargs):
		'''
		takes:
			wb: a WorkingBand type, with a RectangularWaveguide object
				for its tline property.
			d: distance to termination
			Gamma0: reflection coefficient off termination at termination
			initial_offset: initial offset guess, as a fraction of a, 
				(the waveguide width dimension)
			**kwargs: passed to self.function
		'''
		wg = wb.tline
		kwargs.update({'wg':wg,'freq':wb.frequency,'Gamma0':Gamma0})
		
		ParameterizedStandard.__init__(self, \
			function = terminated_translation_offset,\
			parameters = {'delta_a':wg.a*initial_offset, \
						'delta_b':wg.a*initial_offset,\
						'd':d},\
			**kwargs\
			)

class PS_RotatedWaveguide_UnknownLength(ParameterizedStandard):
	'''
	A rotated waveguide of unkown delay length.
	'''
	def __init__(self, wb,d,Gamma0, **kwargs):
		'''
		takes:
			wb: a WorkingBand type, with a RectangularWaveguide object
				for its tline property.
			d: distance to termination
			Gamma0: reflection coefficient off termination at termination
			initial_offset: initial offset guess, as a fraction of a, 
				(the waveguide width dimension)
			**kwargs: passed to self.function
		'''
		wg = wb.tline
		kwargs.update({'wg':wg,'freq':wb.frequency,'delta_a':0,\
			'delta_b':0,'Gamma0':Gamma0})
		
		ParameterizedStandard.__init__(self, \
			function = rotated_waveguide,\
			parameters = {'d':d},\
			**kwargs\
			)


class PS_DelayShort_UnknownLength(ParameterizedStandard):
	'''
	A delay short of unknown length
	
	initial guess for length should be given to constructor
	'''
	def __init__(self, wb,d,**kwargs):
		'''
		takes:
			wb: a WorkingBand type
			d: initial guess for delay short physical length [m]
			**kwargs: passed to self.function
		'''
		ParameterizedStandard.__init__(self, \
			function = wb.delay_short,\
			parameters = {'d':d},\
			**kwargs\
			)
