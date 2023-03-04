import pygame
from pygame.locals import *
from PIL import Image
import numpy


from OpenGL.GL import *
from OpenGL.GLU import *

import math


def read_texture(filename):
    img = Image.open(filename)
    img_data = numpy.array(list(img.getdata()), numpy.int8)
    textID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textID)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    
    img.close()
    return textID


pygame.init()
display = (800, 600)
scree = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
scaled_earth_radius = 6.371

glEnable(GL_DEPTH_TEST)

sphere = gluNewQuadric() #Create new sphere

glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -25 - scaled_earth_radius)    # sets initial zoom so we can see globe


glMatrixMode(GL_MODELVIEW)
gluLookAt(0, -8, 0, 0, 0, 0, 0, 0, 1)
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
glLoadIdentity()

lastPosX = 0
lastPosY = 0
texture = read_texture('earth_texture.jpg')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        # Zoom in and out with mouse wheel
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # wheel rolled up
                glScaled(1.1, 1.1, 1.1)
            if event.button == 5:  # wheel rolled down
                glScaled(0.9, 0.9, 0.9)

        # Rotate with mouse click and drag
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            dx = x - lastPosX
            dy = y - lastPosY
            mouseState = pygame.mouse.get_pressed()
            if mouseState[0]:

                modelView = (GLfloat * 16)()
                mvm = glGetFloatv(GL_MODELVIEW_MATRIX, modelView)

                # To combine x-axis and y-axis rotation
                temp = (GLfloat * 3)()
                temp[0] = modelView[0]*dy + modelView[1]*dx
                temp[1] = modelView[4]*dy + modelView[5]*dx
                temp[2] = modelView[8]*dy + modelView[9]*dx
                norm_xy = math.sqrt(temp[0]*temp[0] + temp[1]
                                    * temp[1] + temp[2]*temp[2])
                glRotatef(math.sqrt(dx*dx+dy*dy),
                        temp[0]/norm_xy, temp[1]/norm_xy, temp[2]/norm_xy)

            lastPosX = x
            lastPosY = y

    keypress = pygame.key.get_pressed()

    # glEnable(GL_DEPTH_TEST)
    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # init model view matrix
    glLoadIdentity()

    # init the view matrix
    glPushMatrix()
    glLoadIdentity()

    # apply the movment 
    if keypress[pygame.K_w]:
        glTranslatef(0,0,0.1)
    if keypress[pygame.K_s]:
        glTranslatef(0,0,-0.1)
    if keypress[pygame.K_d]:
        glTranslatef(-0.1,0,0)
    if keypress[pygame.K_a]:
        glTranslatef(0.1,0,0)

    # multiply the current matrix by the get the new view matrix and store the final vie matrix 
    glMultMatrixf(viewMatrix)
    viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

    # apply view matrix
    glPopMatrix()
    glMultMatrixf(viewMatrix)

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT) #Clear the screen

    glPushMatrix()

    glTranslatef(-1.5, 0, 0) #Move to the place
    # glColor4f(0.5, 0.2, 0.2, 1) #Put color
    # gluSphere(sphere, scaled_earth_radius, 32, 16) #Draw sphere

    gluQuadricTexture(sphere, GL_TRUE)
    # gluQuadricNormals(sphere, GL_TRUE)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)
    glColor3f(0.5, 0.2, 0.2) #Put color
    gluSphere(sphere, scaled_earth_radius, 50, 50)  # may set to sat_class.Re
    glDisable(GL_TEXTURE_2D)
    gluDeleteQuadric(sphere)
    sphere = gluNewQuadric()

    glPopMatrix()

    pygame.display.flip() #Update the screen
    pygame.time.wait(10)

pygame.quit()