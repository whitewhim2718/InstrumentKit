#!/usr/bin/python
# -*- coding: utf-8 -*-
##
# _packets.py: Module for working with ThorLabs packets.
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

## IMPORTS #####################################################################

from instruments.thorlabs import _packets
from instruments.abstract_instruments.instrument import Instrument

## CLASSES #####################################################################

class ThorLabsInstrument(Instrument):

    def __init__(self, filelike):
        super(ThorLabsInstrument, self).__init__(filelike)
        self.terminator = ''
    
    def sendpacket(self, packet):
        self.sendcmd(packet.pack())
        
    def querypacket(self, packet):
        return _packets.ThorLabsPacket.unpack(self.query(packet.pack()))
      
