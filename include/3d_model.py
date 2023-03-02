import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import glutSolidSphere
from OpenGL.GL import shaders
import numpy as np
from glm import *

# Initialize Pygame
pygame.init()

# Set the display size
display = (800, 600)
pygame.display.set_mode(display, pygame.DOUBLEBUF|pygame.OPENGL)

# Set the OpenGL perspective
glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

# Set the initial camera position
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glTranslatef(0.0, 0.0, -5.0)

# Set up lighting
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 1.0, 1.0, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))

# Load the Earth texture
textureSurface = pygame.image.load("earth_texture.jpg")
textureData = pygame.image.tostring(textureSurface, "RGB", 1)
width = textureSurface.get_width()
height = textureSurface.get_height()

# Create the Earth sphere
earthQuadric = gluNewQuadric()
gluQuadricTexture(earthQuadric, GL_TRUE)
gluQuadricNormals(earthQuadric, GL_SMOOTH)
glEnable(GL_TEXTURE_2D)
glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, textureData)
gluSphere(earthQuadric, 1.0, 32, 32)

# Define the satellite position
satellitePosition = (2.0, 0.0, 0.0)

# Create the satellite marker
satelliteMarker = glGenLists(1)
glNewList(satelliteMarker, GL_COMPILE)
glColor3f(1.0, 0.0, 0.0)
glPushMatrix()
glTranslatef(satellitePosition[0], satellitePosition[1], satellitePosition[2])
glutSolidSphere(0.1, 10, 10)
glPopMatrix()
glEndList()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Rotate the Earth
    glRotatef(1, 0.0, 1.0, 0.0)

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    # Draw the Earth
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5.0)
    glRotatef(45, 1.0, 0.0, 0.0)
    glRotatef(pygame.time.get_ticks() / 10, 0.0, 1.0, 0.0)
    gluSphere(earthQuadric, 1.0, 32, 32)

    # Draw the satellite marker
    glCallList(satelliteMarker)

    # Update the screen
    pygame.display.flip()
