import typing

import pygame
from pygame.locals import QUIT

import numpy as np
from math import cos, sin

from settings import *

import cv2


def rotate(vert: typing.Union[list, tuple], xyz: typing.Union[list, tuple]) -> list:
    """
    Rotates given vertex on the X, Y, and Z dimensions.
    """
    x, y, z = xyz
    x_matrix = np.array([[1, 0, 0], [0, cos(x), -sin(x)], [0, sin(x), cos(x)]])

    y_matrix = np.array([[cos(y), 0, sin(y)], [0, 1, 0], [-sin(y), 0, cos(y)]])

    z_matrix = np.array([[cos(z), -sin(z), 0], [sin(z), cos(z), 0], [0, 0, 1]])

    return [round(i) for i in np.array(vert).dot(x_matrix).dot(y_matrix).dot(z_matrix)]


class Shape:
    def __init__(self, mesh, position, rotation, scale, texture=pygame.Surface((50, 50))) -> None:
        self.base_mesh = mesh
        self.mesh = [
            [[[axis * scale for axis in vertex] for vertex in face], texture]
            for face in self.base_mesh
        ]

        self.position = position
        self.rotation = rotation


class Cube(Shape):
    def __init__(self, scale, texture=pygame.Surface((50, 50))) -> None:
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
            texture
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
        render_order = []
        for obj in self.objs:
            for face in obj.mesh:
                projected_vertice = []
                lowest_z = -float("inf")
                for vertex in face[0]:
                    true_vertex = rotate(vertex, obj.rotation)
                    true_vertex = [
                        true_vertex[0] + obj.position[0],
                        true_vertex[1] + obj.position[1],
                        true_vertex[2] + obj.position[2],
                    ]
                    projected_vertice.append(self.project(true_vertex))
                    lowest_z = max(lowest_z, true_vertex[2])
                render_order.append([projected_vertice, face[1], lowest_z])

        def quick_sort(array):
            if len(array) < 2:
                return array
            else:
                pivot = array[0]
                less = [i for i in array[1:] if i[2] >= pivot[2]]
                greater = [i for i in array[1:] if i[2] < pivot[2]]
                return quick_sort(less) + [pivot] + quick_sort(greater)

        render_order = quick_sort(render_order)
        for face in render_order:
            # pygame.draw.polygon(screen, "black", face[0], 3)
            warped = self.warp(face[1], face[0])
            screen.blit(warped[0], warped[1])

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

        x_projected = (self.focal_length * x) / (self.focal_length + z) + 300
        y_projected = (self.focal_length * y) / (self.focal_length + z) + 300

        return x_projected, y_projected

    def warp(self, texture, quad) -> pygame.Surface:
        """
        Takes a `pygame.Surface` as a texture. Returns the texture mapped to a `quad`.

        Credit to @davidpendergast for this function
        """
        out = None

        # Check that quad contains four points
        if len(quad) != 4:
            raise ValueError("quad must contain four points")

        # Get texture size and check if it has alpha channel
        w, h = texture.get_size()
        is_alpha = texture.get_flags() & pygame.SRCALPHA

        # Define source corners for transformation
        src_corners = np.float32([(0, 0), (0, w), (h, w), (h, 0)])
        # Swap x and y coordinates in quad
        quad = [tuple(reversed(p)) for p in quad]

        # Find the bounding box of quad points
        min_x, max_x = float("inf"), -float("inf")
        min_y, max_y = float("inf"), -float("inf")
        for p in quad:
            min_x, max_x = min(min_x, p[0]), max(max_x, p[0])
            min_y, max_y = min(min_y, p[1]), max(max_y, p[1])
        warp_bounding_box = pygame.Rect(
            int(min_x), int(min_y), int(max_x - min_x), int(max_y - min_y)
        )

        # Shift quad so that the top-left corner is at (0, 0)
        shifted_quad = [(p[0] - min_x, p[1] - min_y) for p in quad]
        # Define destination corners for transformation
        dst_corners = np.float32(shifted_quad)

        # Compute perspective transform matrix
        mat = cv2.getPerspectiveTransform(src_corners, dst_corners)

        # Convert texture to numpy array
        orig_rgb = pygame.surfarray.pixels3d(texture)

        # Set flags for cv2.warpPerspective
        flags = cv2.INTER_LINEAR
        # Apply perspective transformation to texture
        out_rgb = cv2.warpPerspective(
            orig_rgb, mat, warp_bounding_box.size, flags=flags
        )

        # Create new surface for output
        if out is None or out.get_size() != out_rgb.shape[0:2]:
            out = pygame.Surface(out_rgb.shape[0:2], pygame.SRCALPHA if is_alpha else 0)

        # Copy numpy array to output surface
        pygame.surfarray.blit_array(out, out_rgb)

        # If texture has alpha channel, apply transformation to alpha channel
        if is_alpha:
            # Convert alpha channel to numpy array
            orig_alpha = pygame.surfarray.pixels_alpha(texture)
            # Apply perspective transformation to alpha channel
            out_alpha = cv2.warpPerspective(
                orig_alpha, mat, warp_bounding_box.size, flags=flags
            )
            # Copy alpha channel numpy array to output surface
            alpha_px = pygame.surfarray.pixels_alpha(out)
            alpha_px[:] = out_alpha
        else:
            # If texture doesn't have alpha channel, set color key
            out.set_colorkey(texture.get_colorkey())

        # Swap x and y coordinates in output bounding box
        return out, pygame.Rect(
            warp_bounding_box.y,
            warp_bounding_box.x,
            warp_bounding_box.h,
            warp_bounding_box.w,
        )
