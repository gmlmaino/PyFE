# coding=utf-8
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QPushButton, QIcon

from libs.Utiles import LeerIni


class Boton(QPushButton):

    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args)

        texto = ''
        if 'texto' in kwargs:
            texto = kwargs['texto']

        self.setText(texto)

        if 'imagen' in kwargs:
            icono = QIcon(kwargs['imagen'])
            self.setIcon(icono)

            if 'tamanio' in kwargs:
                if kwargs['tamanio'] and isinstance(kwargs['tamanio'],QSize):
                    self.setIconSize(kwargs['tamanio'])
            else:
                self.setIconSize(QSize(32,32))

        if 'tooltip' in kwargs:
            self.setToolTip(kwargs['tooltip'])

        if 'autodefault' in kwargs:
            self.setAutoDefault(kwargs['autodefault'])
        else:
            self.setDefault(True)
        self.setDefault(False)


class BotonMain(Boton):

    def __init__(self, *args, **kwargs):
        Boton.__init__(self, *args, **kwargs)
        self.setMinimumHeight(100)
        self.setIconSize(QSize(48,48))

class BotonAceptar(Boton):

    def __init__(self, *args, **kwargs):
        kwargs['texto'] = kwargs['textoBoton'] if 'textoBoton' in kwargs else '&Aceptar'
        kwargs['imagen'] = LeerIni("InicioSistema") + 'imagenes/aceptar.bmp'
        kwargs['tamanio'] = QSize(32,32)
        Boton.__init__(self, *args, **kwargs)

class BotonCerrarFormulario(Boton):

    def __init__(self, *args, **kwargs):
        kwargs['texto'] = kwargs['textoBoton'] if 'textoBoton' in kwargs else '&Cerrar'
        kwargs['imagen'] = LeerIni("InicioSistema") + 'imagenes/log-out.png'
        kwargs['tamanio'] = QSize(32,32)
        Boton.__init__(self, *args, **kwargs)
        self.setDefault(False)