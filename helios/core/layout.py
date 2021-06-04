from abc import ABC, ABCMeta, abstractmethod
import numpy as np

class NetworkLayout(ABC):
    def __init__(self, network, *args, positions = None, **kargs):
        self.network = network
        if(positions is not None):
            self.positions = positions
        else:
            self._positions = np.zeros((self.network.vertex_count(),self.dimensions),dtype=np.float32)
    
    @abstractmethod
    def steps(self, iterations=1):
        ...
    
    @property
    def positions(self):
        return self._positions
    
    @positions.setter
    def positions(self, new_positions):
        #check if it is float32 and dimensions
        self._positions = new_positions
      
    @property
    def dimensions(self):
        return 3
      
class NetworkActor(...):
    @property
    def actors(self):
        return [self.nodes, self.edges]

    # updateCallback



class NetworkLayoutAsync(NetworkLayout, metaclass=ABCMeta):
    @abstractmethod
    def start(self, max_iterations=None):
        ...
    
    @abstractmethod
    def stop(self):
        ...
    
    @abstractmethod
    def wait(self):
        ...

    def steps(self,iterations=1):
        self.start(max_iterations=iterations)
        self.wait()

