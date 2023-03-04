import pygame
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import numpy

from include import Satellite_class
from include import GroundStation_class
from include import Observation_class
from include import satcompute

class Display:
    _sat_list = []
    _sat_commnicate_path = []
    _sat_commnicate_delay = []
    _gs: GroundStation_class.GroundStation
    _gd: Observation_class.Observation
    _qobj = gluNewQuadric()


    # setter of point info
    @classmethod
    def set_point_info(cls, gd, sat_list, sat_commnicate_path, sat_commnicate_delay, gs):
        cls._sat_list = sat_list
        cls._sat_commnicate_path = sat_commnicate_path
        cls._sat_commnicate_delay = sat_commnicate_delay
        cls._gs = gs
        cls._gd = gd


    @classmethod
    def __read_texture(cls, filename):
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
        return textID


    # convert ECI xyz to pygame xyz
    @classmethod
    def __cei_to_pygame_pos(cls, x, y, z):
        pass


    # temp
    @classmethod
    def __draw_sat(cls):
        for s in cls._sat_list:
            x, y, z = satcompute.get_sat_eci_xyz(0, s)

        # Draw a point at the specified XYZ coordinates
            # gluQuadricTexture(qobj, GL_TRUE)

            # gluSphere(qobj, 1, 50, 50)  # may set to sat_class.Re
            glPushMatrix()

            glTranslatef(x, y, z) #Move to the place
            glColor4f(0.5, 0.2, 0.2, 1) #Put color
            gluSphere(cls._qobj, 1.0, 32, 16) #Draw sphere

            glPopMatrix()


    @classmethod
    def display(cls):      # sat_list: list, sat_commnicate_path, sat_commnicate_delay
        pygame.init()
        display = (800, 800)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption('Satellite Path')
        pygame.key.set_repeat(1, 10)    # allows press and hold of buttons
        gluPerspective(40, (display[0]/display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)    # sets initial zoom so we can see globe
        lastPosX = 0
        lastPosY = 0
        texture = cls.__read_texture('earth_texture.jpg')

        while True:
            for event in pygame.event.get():    # user avtivities are called events

                # Exit cleanly if user quits window
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                # Rotation with arrow keys
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        glRotatef(1, 0, 1, 0)
                    if event.key == pygame.K_RIGHT:
                        glRotatef(1, 0, -1, 0)
                    if event.key == pygame.K_UP:
                        glRotatef(1, -1, 0, 0)
                    if event.key == pygame.K_DOWN:
                        glRotatef(1, 1, 0, 0)

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

            # Creates Sphere and wraps texture
            glEnable(GL_DEPTH_TEST)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            gluQuadricTexture(cls._qobj, GL_TRUE)
            gluQuadricNormals(cls._qobj, GL_TRUE)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture)
            gluSphere(cls._qobj, 1, 50, 50)  # may set to sat_class.Re
            # gluDeleteQuadric(cls._qobj)
            glDisable(GL_TEXTURE_2D)

            # cls.__draw_sat()

            # Displays pygame window
            pygame.display.flip()
            pygame.time.wait(10)
