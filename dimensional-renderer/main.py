import typing

import pygame
from pygame.locals import QUIT

import numpy as np
from math import cos, sin

from settings import *

pygame.init()

screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Dimensional Renderer")


def rotate(vert: typing.Union[list, tuple], xyz: typing.Union[list, tuple]) -> list:
    """
    Rotates given vertex on the X, Y, and Z dimensions.
    """
    x, y, z = xyz
    x_matrix = np.array([[1, 0, 0], [0, cos(z), -sin(x)], [0, sin(x), cos(x)]])

    y_matrix = np.array([[cos(y), 0, sin(y)], [0, 1, 0], [-sin(y), 0, cos(y)]])

    z_matrix = np.array([[cos(z), -sin(z), 0], [sin(z), cos(z), 0], [0, 0, 1]])

    return [round(i) for i in np.array(vert).dot(x_matrix).dot(y_matrix).dot(z_matrix)]


class Shape:
    def __init__(self, mesh, position, rotation, scale) -> None:
        self.base_mesh = mesh
        self.mesh = [
            [[axis * scale for axis in vertex] for vertex in face]
            for face in self.base_mesh
        ]

        self.position = position
        self.rotation = rotation


class Cube(Shape):
    def __init__(self, scale) -> None:
        super().__init__(
            [
                [
                    [-0.5, -0.5, -0.5],
                    [0.5, -0.5, -0.5],
                    [0.5, 0.5, -0.5],
                    [-0.5, 0.5, -0.5],
                ],
                [
                    [0.5, -0.5, -0.5],
                    [0.5, -0.5, 0.5],
                    [0.5, 0.5, 0.5],
                    [0.5, 0.5, -0.5],
                ],
                [
                    [0.5, -0.5, 0.5],
                    [-0.5, -0.5, 0.5],
                    [-0.5, 0.5, 0.5],
                    [0.5, 0.5, 0.5],
                ],
                [
                    [-0.5, -0.5, 0.5],
                    [-0.5, -0.5, -0.5],
                    [-0.5, 0.5, -0.5],
                    [-0.5, 0.5, 0.5],
                ],
                [
                    [-0.5, -0.5, 0.5],
                    [0.5, -0.5, 0.5],
                    [0.5, -0.5, -0.5],
                    [-0.5, -0.5, -0.5],
                ],
                [
                    [-0.5, 0.5, -0.5],
                    [0.5, 0.5, -0.5],
                    [0.5, 0.5, 0.5],
                    [-0.5, 0.5, 0.5],
                ],
            ],
            [0, 0, 0],
            [0, 0, 0],
            scale,
        )


class Camera:
    """
    Renders all `objs` onto the screen. Uses weak perspective projection. It takes in quads.
    """

    def __init__(self, objs: list):
        self.objs = objs

        self.scroll = [0, 0, 0]
        self.rotation = [0, 0, 0]

        self.focal_length = 60

    def render(self, screen) -> None:
        """
        Will draw objs to the screen. Should be recalled every frame. Handles projection, texturing,
        and ordering.
        """
        for obj in self.objs:
            for face in obj.mesh:
                projected_vertice = [self.project([vertex[0]+obj.position[0], vertex[1]+obj.position[1], vertex[2]+obj.position[2]]) for vertex in face]
                pygame.draw.polygon(screen, "black", projected_vertice, 2)

    def project(self, vertex) -> tuple:
        """
        Backend method to calculate the 2d position of a point. Bakes in camera offset and rotaion
        as well.
        """
        # Camera transformations
        real_vert = rotate(vertex, self.rotation)
        real_vert[0] -= self.scroll[0]
        real_vert[1] -= self.scroll[1]
        real_vert[2] -= self.scroll[2]

        real_vert = rotate(real_vert, self.rotation)

        # Projection
        x, y, z = real_vert

        x_projected = (self.focal_length * x) / (self.focal_length + z)
        y_projected = (self.focal_length * y) / (self.focal_length + z)

        return x_projected, y_projected

    def warp(self, texture, quad) -> pygame.Surface:
        """
        Takes a `pygame.Surface` as a texture. Returns the texture mapped to a `quad`.
        """
        pass

camera = Camera([Cube(60)])

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:
            running = False

    screen.fill(BACKGROUND_COLOR)

    # Rendering
    camera.render(screen)

    pygame.display.flip()
