import typing

import pygame
from pygame.locals import QUIT

import numpy as np
from math import cos, sin

pygame.init()
DISPLAYSURF = pygame.display.set_mode((400, 300))
pygame.display.set_caption('The Sky Is Falling')


def rotate(vert: typing.Union[list, tuple], xyz: typing.Union[list, tuple]) -> list:
    """
    Rotates given vertice on the X, Y, and Z dimensions.
    """
    x, y, z = xyz
    x_matrix = np.array([[1, 0, 0],
                         [0, cos(z), -sin(x)],
                         [0, sin(x), cos(x)]])

    y_matrix = np.array([[cos(y), 0, sin(y)],
                         [0, 1, 0],
                         [-sin(y), 0, cos(y)]])

    z_matrix = np.array([[cos(z), -sin(z), 0],
                         [sin(z), cos(z), 0],
                         [0, 0, 1]])

    return [round(i) for i in np.array(vert).dot(x_matrix).dot(y_matrix).dot(z_matrix)]


class Camera:
    """
    Renders all `objs` onto the screen. Uses weak perspective projection. It takes in quads.
    """

    def __init__(self, objs: list):
        self.objs = objs

        self.scroll = [0, 0, 0]
        self.rotation = [0, 0, 0]

    def render(self, screen):
        """
        Will draw objs to the screen. Should be recalled every frame. Handles projection, texturing, 
        and ordering.
        """
        pass

    def project(self, vertice):
        """
        Backend method to calculate the 2d position of a point. Bakes in camera offset and rotaion 
        as well.
        """
        real_vert = rotate(vertice, self.rotation)
        real_vert[0] -= self.scroll[0]
        real_vert[1] -= self.scroll[1]
        real_vert[2] -= self.scroll[2]

        real_vert = rotate(real_vert, self.rotation)

    def warp(self, texture, quad) -> pygame.Surface:
        """
        Takes a `pygame.Surface` as a texture. Returns the texture mapped to a `quad`.
        """
        pass


running = True
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    pygame.display.update()
