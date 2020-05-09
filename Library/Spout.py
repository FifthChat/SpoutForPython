import cv2 as cv
import numpy as np
import glfw
import Library.SpoutSDK as SpoutSDK
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.GLU import *

class Spout() :
    """
    Args:
        windowWidth、widowHeight: 显示图形窗口的大小。
        displayMode: 选择窗口的显示模式。'Send'为显示发送图像数据，'Receive'为显示接受图像数据。
        displayWindow: 是否显示图形窗口。
    """
    
    def __init__(self, windowWidth: int = 640, windowHeight: int = 480, displayMode: str = "Send", displayWindow: bool = True):
        """
        Args:
            windowWidth、widowHeight: 显示图形窗口的大小。
            displayMode: 选择窗口的显示模式。'Send'为显示发送图像数据，'Receive'为显示接受图像数据。
            displayWindow: 是否显示图形窗口。
        """
        self.__windowWidth = windowWidth
        self.__windowHeight = windowHeight
        self.__displayWindow = displayWindow

        if displayMode == "Receive" or displayMode == "Send":
            self.__displayMode = displayMode
        else:
            self.__displayMode = "Send"

        self.__display = (self.__windowWidth, self.__windowHeight)

        if not glfw.init():
            return
        glfw.window_hint(glfw.VISIBLE, self.__displayWindow)
        self.__window = glfw.create_window(self.__windowWidth, self.__windowHeight, "Spout: " + self.__displayMode, None, None)
        glfw.set_input_mode(self.__window, glfw.STICKY_KEYS, GL_TRUE)
        if not self.__window:
            glfw.terminate()
            return
        glfw.make_context_current(self.__window)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.__windowWidth, self.__windowHeight, 0, 1, -1)
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_TEXTURE_2D)

    def receiverInit(self, receive_name: str, imgType: str = 'RGBA', imgDataType: str = 'INT8') -> bool:
        """
            初始化接收。返回操作是否成功，若操作失败，第二返回值为失败描述。

            Args:
                receive_name: 接收Spout名称。
                imgType : 像素数据的颜色格式。可选参数 [ 'RGBA', 'RGB', 'ALPHA', 'LUMINANCE', 'LUMINANCEALPHA' ]
                imgDataType : 像素数据的数据类型。可选参数 [ 'INT8', 'Float32' ]
        """

        if imgType == 'RGBA' :
            self.__receiveType = GL_RGBA
        elif imgType == 'RGB' :
            self.__receiveType = GL_RGB
        elif imgType == 'ALPHA' :
            self.__receiveType = GL_ALPHA
        elif imgType == 'LUMINANCE':
            self.__receiveType = GL_LUMINANCE
        elif imgType == 'LUMINANCEALPHA':
            self.__receiveType = GL_LUMINANCE_ALPHA
        else :
            return False, 'imgType parameter is incorrect.'

        if imgDataType == 'INT8':
            self.__receiveDataType = GL_UNSIGNED_BYTE
        elif imgDataType == 'Float32':
            self.__receiveDataType = GL_FLOAT
        else:
            return False, 'imgDataType parameter is incorrect.'

        self.__receive_name = receive_name
        self.__spout_receiver = SpoutSDK.SpoutReceiver()
        self.__receiveWidth = self.__spout_receiver.GetWidth(self.__receive_name)
        self.__receiveHeight = self.__spout_receiver.GetHeight(self.__receive_name)
        self.__spout_receiver.pyCreateReceiver(self.__receive_name, self.__receiveWidth, self.__receiveHeight, False)

        self.__texture_receive_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.__texture_receive_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0,  self.__receiveType, self.__receiveWidth, self.__receiveHeight, 0,  self.__receiveType, self.__receiveDataType, None ) 
        glBindTexture(GL_TEXTURE_2D, 0)
        return True, ""

    def senderInit(self, send_name: str):
        """
            初始化发送。

            Args:
                send_name: 发送Spout名称。
        """

        self.__send_name = send_name
        self.__senderWidth = -1 
        self.__senderHeight = -1

        self.__spout_sender = SpoutSDK.SpoutSender()
        self.__spout_sender.CreateSender(self.__send_name,self.__windowWidth,self.__windowHeight, 0)

    def receiverData(self):
        """
            接收Spout图像。返回numpy数组。
        """
        
        if self.__receiveWidth != self.__spout_receiver.GetWidth(self.__receive_name) or self.__receiveHeight != self.__spout_receiver.GetHeight(self.__receive_name) :

            self.__spout_receiver.pyCreateReceiver(self.__receive_name, self.__receiveWidth, self.__receiveHeight, False)

            self.__texture_receive_id = glGenTextures(1)

            glBindTexture(GL_TEXTURE_2D, self.__texture_receive_id)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

            self.__receiveWidth = self.__spout_receiver.GetWidth(self.__receive_name)
            self.__receiveHeight = self.__spout_receiver.GetHeight(self.__receive_name)

            glTexImage2D(GL_TEXTURE_2D, 0, self.__receiveType, self.__receiveWidth, self.__receiveHeight, 0, self.__receiveType, self.__receiveDataType, None ) 
            glBindTexture(GL_TEXTURE_2D, 0)

        self.__spout_receiver.pyReceiveTexture(self.__receive_name, self.__receiveWidth, self.__receiveHeight, self.__texture_receive_id.item(), GL_TEXTURE_2D, False, 0)

        glBindTexture(GL_TEXTURE_2D, self.__texture_receive_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        self.__changeViewerMode()
        self.__receiveMode()

        self.__receiverTexture = glGetTexImage(GL_TEXTURE_2D, 0, self.__receiveType, self.__receiveDataType, outputType=None)
        glBindTexture(GL_TEXTURE_2D, 0)
        self.__receiverTexture.shape = (self.__receiverTexture.shape[1], self.__receiverTexture.shape[0], self.__receiverTexture.shape[2])
        
        return self.__receiverTexture

    def senderData(self, send_img_data, imgType: str = 'RGBA', imgDataType: str = 'INT8') -> bool:
        """
            发送Spout图像。返回操作是否成功，若操作失败，第二返回值为失败描述。

            Args:
                send_img_data : 发送的图像数据，数据类型numpy数组。
                imgType : 像素数据的颜色格式。可选参数 [ 'RGBA', 'RGB', 'ALPHA', 'LUMINANCE', 'LUMINANCEALPHA' ]
                imgDataType : 像素数据的数据类型。可选参数 [ 'INT8', 'Float32' ]
        """

        if send_img_data.size == 0 :

            self.__zero()

            return False, "send_img_data is empty."

        if imgType == 'RGBA' :
            self.__sendType = GL_RGBA
        elif imgType == 'RGB' :
            self.__sendType = GL_RGB
        elif imgType == 'ALPHA' :
            self.__sendType = GL_ALPHA
        elif imgType == 'LUMINANCE':
            self.__sendType = GL_LUMINANCE
        elif imgType == 'LUMINANCEALPHA':
            self.__sendType = GL_LUMINANCE_ALPHA
        else :
            
            self.__zero()

            return False, 'imgType parameter is incorrect.'

        if imgDataType == 'INT8':
            self.__sendDataType = GL_UNSIGNED_BYTE
        elif imgDataType == 'Float32':
            self.__sendDataType = GL_FLOAT
        else:
            
            self.__zero()

            return False, 'imgDataType parameter is incorrect.'

        self.__sendImageData = send_img_data

        if self.__senderWidth != send_img_data.shape[1] or self.__senderHeight != send_img_data.shape[0] :
            self.__senderWidth = send_img_data.shape[1]
            self.__senderHeight = send_img_data.shape[0]

        try:
            self.__texture_sender_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.__texture_sender_id)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        
            glTexImage2D( GL_TEXTURE_2D, 0, self.__sendType, self.__senderWidth, self.__senderHeight, 0, self.__sendType, self.__sendDataType, self.__sendImageData ) 
            self.__spout_sender.SendTexture(self.__texture_sender_id.item(), GL_TEXTURE_2D, self.__senderWidth, self.__senderHeight, False, 0)
        except:
            self.__zero()
            return False, "Image Format maybe wrong.Please check your image data."

        self.__sendMode()
        return True, ""

    def __changeViewerMode(self):
        #self.__displayMode = "receive" 
        if glfw.get_key(self.__window, glfw.KEY_S) == glfw.PRESS:
            self.__displayMode = "Send"
        elif glfw.get_key(self.__window, glfw.KEY_R) == glfw.PRESS:
            self.__displayMode = "Receive"

    def __receiveMode(self):
        if self.__displayMode == "Receive":
            glfw.set_window_title(self.__window, "Spout: " + self.__displayMode + " Texture")

            if self.__receiveWidth == 0 and self.__receiveHeight == 0:
                if not glfw.window_should_close(self.__window):
                    
                    glActiveTexture(GL_TEXTURE0)
                    glClear(GL_COLOR_BUFFER_BIT  | GL_DEPTH_BUFFER_BIT )
                    glLoadIdentity()
                    glBegin(GL_QUADS)
                    glTexCoord2f(0, 0)
                    glVertex2f(0, 0)
                    glTexCoord2f(1, 0)
                    glVertex2f(1, 0)
                    glTexCoord2f(1, 1)
                    glVertex2f(1, 1)
                    glTexCoord2f(0, 1)
                    glVertex2f(0, 1)
                    glEnd()
                    glfw.swap_buffers(self.__window)
                    glfw.poll_events()
                else:
                    glfw.destroy_window(self.__window)
                    glfw.terminate()
            
            else:
                if not glfw.window_should_close(self.__window):
                    left = 0
                    top = 0
                    width = self.__windowWidth
                    height = self.__windowHeight
                    
                    sx = self.__windowWidth / self.__receiveWidth 
                    sy = self.__windowHeight / self.__receiveHeight 
                    if sx > sy:
                        width *= sy / sx
                        left = (self.__windowWidth - width) / 2
                    else:
                        height *= sx / sy  
                        top = (self.__windowHeight - height) / 2
                    glActiveTexture(GL_TEXTURE0)
                    glClear(GL_COLOR_BUFFER_BIT  | GL_DEPTH_BUFFER_BIT )
                    glLoadIdentity()
                    glBegin(GL_QUADS)
                    glTexCoord2f(0, 0)
                    glVertex2f(left, top)
                    glTexCoord2f(1, 0)
                    glVertex2f(left + width, top)
                    glTexCoord2f(1, 1)
                    glVertex2f(left + width, top + height)
                    glTexCoord2f(0, 1)
                    glVertex2f(left, top + height)
                    glEnd()
                    glfw.swap_buffers(self.__window)
                    glfw.poll_events()
                else:
                    glfw.destroy_window(self.__window)
                    glfw.terminate()

    def __sendMode(self):
        if self.__displayMode == "Send":
            glfw.set_window_title(self.__window, "Spout: " + self.__displayMode + " Texture")

            if self.__receiveWidth == 0 and self.__receiveHeight == 0:
                if not glfw.window_should_close(self.__window):
                    glActiveTexture(GL_TEXTURE0)
                    glClear(GL_COLOR_BUFFER_BIT  | GL_DEPTH_BUFFER_BIT )
                    glLoadIdentity()
                    glBegin(GL_QUADS)
                    glTexCoord2f(0, 0)
                    glVertex2f(0, 0)
                    glTexCoord2f(1, 0)
                    glVertex2f(1, 0)
                    glTexCoord2f(1, 1)
                    glVertex2f(1, 1)
                    glTexCoord2f(0, 1)
                    glVertex2f(0, 1)
                    glEnd()
                    glfw.swap_buffers(self.__window)
                    glfw.poll_events()
                else:
                    glfw.destroy_window(self.__window)
                    glfw.terminate()
            
            else:
                if not glfw.window_should_close(self.__window):
                    left = 0
                    top = 0
                    width = self.__windowWidth
                    height = self.__windowHeight

                    sx = self.__windowWidth / self.__senderWidth 
                    sy = self.__windowHeight / self.__senderHeight 
                    if sx > sy:
                        width *= sy / sx
                        left = (self.__windowWidth - width) / 2
                    else:
                        height *= sx / sy  
                        top = (self.__windowHeight - height) / 2
                    glActiveTexture(GL_TEXTURE0)
                    glClear(GL_COLOR_BUFFER_BIT  | GL_DEPTH_BUFFER_BIT )
                    glLoadIdentity()
                    glBegin(GL_QUADS)
                    glTexCoord2f(0, 0)
                    glVertex2f(left, top)
                    glTexCoord2f(1, 0)
                    glVertex2f(left + width, top)
                    glTexCoord2f(1, 1)
                    glVertex2f(left + width, top + height)
                    glTexCoord2f(0, 1)
                    glVertex2f(left, top + height)
                    glEnd()
                    glfw.swap_buffers(self.__window)
                    glfw.poll_events()
                else:
                    glfw.destroy_window(self.__window)
                    glfw.terminate()

    def __zero(self):

        zero = np.zeros((640, 480, 3))
        self.__texture_sender_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.__texture_sender_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGB, 640, 480, 0, GL_RGB, GL_FLOAT, zero ) 
        self.__sendMode()