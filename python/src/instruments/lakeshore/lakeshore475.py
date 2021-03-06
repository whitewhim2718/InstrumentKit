#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# lakeshore475.py: Python class for the Lakeshore 475 Gaussmeter
##
# © 2013 Steven Casagrande (scasagrande@galvant.ca).
#
# This file is a part of the InstrumentKit project.
# Licensed under the AGPL version 3.
##
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##
##

## FEATURES ####################################################################

from __future__ import division

## IMPORTS #####################################################################

import quantities as pq
from flufl.enum import IntEnum

from instruments.generic_scpi import SCPIInstrument
from instruments.util_fns import assume_units

## CONSTANTS ###################################################################

LAKESHORE_FIELD_UNITS = {
    1: pq.gauss,
    2: pq.tesla,
    3: pq.oersted,
    4: pq.CompoundUnit('A/m')
}

LAKESHORE_TEMP_UNITS = {
    1: pq.celsius,
    2: pq.kelvin
}

LAKESHORE_FIELD_UNITS_INV = dict((v,k) for k,v in 
                                       LAKESHORE_FIELD_UNITS.items())
LAKESHORE_TEMP_UNITS_INV = dict((v,k) for k,v in 
                                       LAKESHORE_TEMP_UNITS.items())

## CLASSES #####################################################################

class Lakeshore475(SCPIInstrument):
    '''
    The Lakeshore475 is a DSP Gaussmeter with field ranges from 35mG to 350kG.
    
    Example usage:
    
    >>> import instruments as ik
    >>> import quantities as pq
    >>> gm = ik.lakeshore.Lakeshore475.open_gpibusb('/dev/ttyUSB0', 1)
    >>> print gm.field
    >>> gm.field_units = pq.tesla
    >>> gm.field_setpoint = 0.05 * pq.tesla
    '''

    ## ENUMS ##
    
    class Mode(IntEnum):
        dc   = 1
        rms  = 2
        peak = 3
        
    class Filter(IntEnum):
        wide    = 1
        narrow  = 2
        lowpass = 3
        
    class PeakMode(IntEnum):
        periodic = 1
        pulse    = 2
    
    class PeakDisplay(IntEnum):
        positive = 1
        negative = 2
        both     = 3

    ## PROPERTIES ##

    @property
    def field(self):
        '''
        Read field from connected probe.
        
        :type: `~quantities.Quantity`
        '''
        return float(self.query('RDGFIELD?')) * self.field_units
        
    @property
    def field_units(self):
        '''
        Gets/sets the units of the Gaussmeter.
        
        Acceptable units are Gauss, Tesla, Oersted, and Amp/meter.
        
        :type: `~quantities.UnitQuantity`
        '''
        value = int(self.query('UNIT?'))
        return LAKESHORE_FIELD_UNITS[value]
    @field_units.setter
    def field_units(self, newval):
        if isinstance(newval, pq.unitquantity.UnitQuantity):
            if newval in LAKESHORE_FIELD_UNITS_INV:
                self.sendcmd('UNIT ' + LAKESHORE_FIELD_UNITS_INV[newval])
            else:
                raise ValueError('Not an acceptable Python quantities object')
        else:
            raise TypeError('Field units must be a Python quantity')
        
    @property
    def temp_units(self):
        '''
        Gets/sets the temperature units of the Gaussmeter.
        
        Acceptable units are celcius and kelvin.
        
        :type: `~quantities.UnitQuantity`
        '''
        value = int(self.query('TUNIT?'))
        return LAKESHORE_TEMP_UNITS[value]
    @temp_units.setter
    def temp_units(self, newval):
        if isinstance(newval, pq.unitquantity.UnitQuantity):
            if newval in LAKESHORE_TEMP_UNITS_INV:
                self.sendcmd('TUNIT ' + LAKESHORE_TEMP_UNITS_INV[newval])
            else:
                raise TypeError('Not an acceptable Python quantities object')
        else:
            raise TypeError('Temperature units must be a Python quantity')

    @property
    def field_setpoint(self):
        '''
        Gets/sets the final setpoint of the field control ramp.

        :units: As specified (if a `~quantities.Quantity`) or assumed to be
            of units Gauss.
        :type: `~quantities.Quantity` with units Gauss
        '''
        value = self.query('CSETP?').strip()
        units = self.field_units
        return float(value) * units
    @field_setpoint.setter
    def field_setpoint(self, newval):
        units = self.field_units
        newval = float(assume_units(newval, pq.gauss).rescale(units).magnitude)

        self.sendcmd('CSETP {}'.format(newval))
        
    @property
    def field_control_params(self):
        '''
        Gets/sets the parameters associated with the field control ramp.
        These are the P, I, ramp rate, and control slope limit.
        
        :type: `tuple` of 2 `float` and 2 `~quantities.Quantity`
        '''
        params = self.query('CPARAM?').strip().split(',')
        params = [float(x) for x in params]
        params[2] = params[2] * self.field_units / pq.minute
        params[3] = params[3] * pq.volt / pq.minute
        
        return tuple(params)
    @field_control_params.setter
    def field_control_params(self, newval):
        if not isinstance(newval, tuple):
            raise TypeError('Field control parameters must be specified as '
                            ' a tuple')
        newval = list(newval)
        newval[0] = float(newval[0])
        newval[1] = float(newval[1])

        unit = self.field_units / pq.minute
        newval[2] = float(assume_units(newval[2], unit).rescale(unit).magnitude)
        unit = pq.volt / pq.minute
        newval[3] = float(assume_units(newval[3], unit).rescale(unit).magnitude)

        self.sendcmd('CPARAM {},{},{},{}'.format(newval[0],
                                                 newval[1],
                                                 newval[2],
                                                 newval[3],
                                                 ))
    
    @property
    def p_value(self):
        '''
        Gets/sets the P value for the field control ramp.
        
        :type: `float`
        '''
        return self.field_control_params[0]
    @p_value.setter
    def p_value(self, newval):
        newval = float(newval)
        values = list(self.field_control_params)
        values[0] = newval
        self.field_control_params = tuple(values)
    
    @property
    def i_value(self):
        '''
        Gets/sets the I value for the field control ramp.
        
        :type: `float`
        '''
        return self.field_control_params[1]
    @i_value.setter
    def i_value(self, newval):
        newval = float(newval)
        values = list(self.field_control_params)
        values[1] = newval
        self.field_control_params = tuple(values)
    
    @property
    def ramp_rate(self):
        '''
        Gets/sets the ramp rate value for the field control ramp.

        :units: As specified (if a `~quantities.Quantity`) or assumed to be
            of current field units / minute.
        :type: `~quantities.Quantity`
        '''
        return self.field_control_params[2]
    @ramp_rate.setter
    def ramp_rate(self, newval):
        unit = self.field_units / pq.minute
        newval = float(assume_units(newval, unit).rescale(unit).magnitude)
        values = list(self.field_control_params)
        values[2] = newval
        self.field_control_params = tuple(values)
        
    @property
    def control_slope_limit(self):
        '''
        Gets/sets the I value for the field control ramp.

        :units: As specified (if a `~quantities.Quantity`) or assumed to be
            of units volt / minute.
        :type: `~quantities.Quantity`
        '''
        return self.field_control_params[3]
    @control_slope_limit.setter
    def control_slope_limit(self, newval):
        unit = pq.volt / pq.minute
        newval = float(assume_units(newval, unit).rescale(unit).magnitude)
        values = list(self.field_control_params)
        values[3] = newval
        self.field_control_params = tuple(values)
        
    @property
    def control_mode(self):
        '''
        Gets/sets the control mode setting. False corresponds to the field
        control ramp being disables, while True enables the closed loop PI
        field control.
        
        :type: `bool`
        '''
        return (self.query('CMODE?').strip() is '1')
    @control_mode.setter
    def control_mode(self, newval):
        if not isinstance(newval, bool):
            raise TypeError('Control mode property must be specified as a bool')
        if (newval):
            self.sendcmd('CMODE 1')
        else:
            self.sendcmd('CMODE 0')
        
    ## METHODS ##

    def change_measurement_mode(self, mode, resolution,
                                filter_type, peak_mode, peak_disp):
        # TODO: almost all of this method is checking types
        #       and validity; absorb this into an enum, perhaps?
        '''
        Change the measurement mode of the Gaussmeter.
        
        :param mode: The desired measurement mode.
        :type mode: `Lakeshore475.Mode`
        
        :param `int` resolution: Digit resolution of the measured field. One of
            `{3|4|5}`.
        
        :param filter_type: Specify the signal filter 
            used by the instrument. Available types include wide band, narrow 
            band, and low pass.
        :type filter_type: `Lakeshore475.Filter`
        
        :param peak_mode: Peak measurement mode to be 
            used.
        :type peak_mode: `Lakeshore475.PeakMode`
        
        :param peak_disp: Peak display mode to be 
            used.
        :type peak_disp: `Lakeshore475.PeakDisplay`
        '''
        if not isinstance(mode, EnumValue) or \
                (mode.enum is not Lakeshore475.Mode):
            raise TypeError("Mode setting must be a "
                              "`Lakeshore475.Mode` value, got {} "
                              "instead.".format(type(mode)))
        if not isinstance(resolution, int):
            raise TypeError('Parameter "resolution" must be an integer.')
        if not isinstance(filter_type, EnumValue) or \
                (filter_type.enum is not Lakeshore475.Filter):
            raise TypeError("Filter type setting must be a "
                              "`Lakeshore475.Filter` value, got {} "
                              "instead.".format(type(filter_type)))
        if not isinstance(peak_mode, EnumValue) or \
                (peak_mode.enum is not Lakeshore475.PeakMode):
            raise TypeError("Filter type setting must be a "
                              "`Lakeshore475.PeakMode` value, got {} "
                              "instead.".format(type(peak_mode)))
        if not isinstance(peak_disp, EnumValue) or \
                (peak_disp.enum is not Lakeshore475.PeakDisplay):
            raise TypeError("Filter type setting must be a "
                              "`Lakeshore475.PeakDisplay` value, got {} "
                              "instead.".format(type(peak_disp)))      

        mode = mode.value
        filter_type = filter_type.value
        peak_mode = peak_mode.value
        peak_disp = peak_disp.value

        # Parse the resolution
        if resolution in xrange(3, 6):
            resolution = resolution - 2
        else:
            raise ValueError('Only 3,4,5 are valid resolutions.')
            
        self.sendcmd('RDGMODE {},{},{},{},{}'.format(mode,
                                                     resolution,
                                                     filter_type,
                                                     peak_mode, 
                                                     peak_disp,
                                                     ))
    

