# utility functions

from DCTopo import FatTreeTopo
from mininet.util import makeNumeric
from DCRouting import HashedRouting

TOPOS = {'ft': FatTreeTopo}
ROUTING = {'ECMP' : HashedRouting}


def buildTopo(topo):
    topo_name, topo_param1,topo_param2 = topo.split( ',' )
    return TOPOS[topo_name](makeNumeric(topo_param1),makeNumeric(topo_param2))


def getRouting(routing, topo):
    return ROUTING[routing](topo)
