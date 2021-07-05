from abc import ABC, ABCMeta, abstractmethod


class NetworkLayout(ABC):
    @abstractmethod
    def steps(self, iterations=1):
        ...

    @property
    def positions(self):
        return self._super_actor.positions

    @positions.setter
    def positions(self, new_positions):
        # check if it is float32 and dimensions
        self._positions = new_positions

    def update_in_vtk(self):
        self._super_actor.positions = self._positions
        self._super_actor.update()
        self.window.Render()


class NetworkLayoutAsync(NetworkLayout, metaclass=ABCMeta):
    @abstractmethod
    def start(self, max_iterations=None):
        ...

    @abstractmethod
    def stop(self):
        ...

    def __del__(self):
        self.stop()


