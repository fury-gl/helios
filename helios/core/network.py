from abc import ABC, abstractmethod
import numpy as np


class Network(ABC):
    @abstractmethod
    def vertex_count():
        ...
    @abstractmethod
    def edge_count():
        ...
    @abstractmethod
    def edges():
        ...
    @abstractmethod
    def vertices():
        ...
    @abstractmethod
    def neighbors_of_vertex():
        ...
    @abstractmethod
    def edge_properties():
        ...
    @abstractmethod
    def vertex_properties():
        ...
    @abstractmethod
    def vertex_properties():
        ...
    @abstractmethod
    def add_edges():
        ...
    @abstractmethod
    def add_vertices():
        ...
    @abstractmethod
    def delete_edges():
        ...
    @abstractmethod
    def delete_vertices():
        ...
