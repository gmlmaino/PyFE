# coding=utf-8
import decimal

from PyQt4.QtCore import QSize
from PyQt4.QtGui import QVBoxLayout, QTabWidget, QWidget, QGridLayout, QHBoxLayout, QLineEdit, QCheckBox, QComboBox

from libs import Ventanas
from libs.Botones import Boton
from libs.Checkbox import CheckBox
from libs.EntradaTexto import EntradaTexto
from libs.Etiquetas import Etiqueta
from libs.Grillas import Grilla
from libs.Utiles import EsVerdadero, inicializar_y_capturar_excepciones
from vistas.VistaBase import VistaBase


class ABM(VistaBase):

    #diccionario que guarda los controles que se agreguen al abm
    controles = {}

    #modelo sobre el que se hace el abm
    model = None

    #indica si es un alta o una modificacion
    tipo = "A"

    #campos a mostrar en la grilla
    camposAMostrar = None

    #condicion para filtrar la tabla
    condicion = None

    #limite de registros
    limite = 100

    #orden de busqueda
    ordenBusqueda = None

    #campo
    campoClave = None

    def __init__(self, *args, **kwargs):
        VistaBase.__init__(self, *args, **kwargs)
        self.controles = {}
        self.initUi()

    @inicializar_y_capturar_excepciones
    def initUi(self, *args, **kwargs):
        self.resize(906, 584)
        nombre_tabla = self.model._meta.table_name.title() if self.model else ''
        self.setWindowTitle("ABM de {}".format(nombre_tabla))
        self.verticalLayout = QVBoxLayout(self)
        self.lblTitulo = Etiqueta(tamanio=15, texto="ABM de {}".format(nombre_tabla))
        self.verticalLayout.addWidget(self.lblTitulo)

        self.tabWidget = QTabWidget()
        self.tabLista = QWidget()
        self.gridLayout = QGridLayout(self.tabLista)

        self.lineEditBusqueda = EntradaTexto(self.tabLista, placeholderText="Busqueda")
        self.lineEditBusqueda.setObjectName("lineEditBusqueda")
        self.gridLayout.addWidget(self.lineEditBusqueda, 0, 0, 1, 1)

        self.tableView = Grilla(self.tabLista)
        self.tableView.setObjectName("tableView")
        self.tableView.enabled = True

        # extraigo los nombres de las columnas
        self.tableView.cabeceras = [x.column_name.capitalize() for x in self.camposAMostrar]
        self.tableView.ArmaCabeceras()
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.BotonesAdicionales()

        self.btnAgregar = Boton(self.tabLista, imagen="imagenes/nuevo.png", tamanio=QSize(32,32),
                                tooltip='Agrega nuevo registro')
        self.btnAgregar.setObjectName("btnAgregar")
        self.horizontalLayout.addWidget(self.btnAgregar)

        self.btnEditar = Boton(self.tabLista, imagen="imagenes/modificar.png", tamanio=QSize(32,32),
                               tooltip='Modifica registro')
        self.btnEditar.setObjectName("btnEditar")
        self.horizontalLayout.addWidget(self.btnEditar)

        self.btnBorrar = Boton(self.tabLista, imagen="imagenes/delete.png", tamanio=QSize(32,32),
                               tooltip='Borrar registro')
        self.btnBorrar.setObjectName("btnBorrar")
        self.horizontalLayout.addWidget(self.btnBorrar)

        self.btnCerrar = Boton(self.tabLista, imagen="imagenes/log-out.png", tamanio=QSize(32,32),
                               tooltip='Cerrar ABM')
        self.btnCerrar.setObjectName("btnCerrar")
        self.horizontalLayout.addWidget(self.btnCerrar)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)

        self.tabWidget.addTab(self.tabLista, "Lista")
        self.tabDetalle = QWidget()
        self.tabWidget.addTab(self.tabDetalle, "Detalle")
        self.tabDetalle.setEnabled(False)

        self.verticalLayout.addWidget(self.tabWidget)

        self.ArmaDatos()
        self.ArmaTabla()
        self.ConectaWidgets()

    def BotonesAdicionales(self):
        pass

    def ArmaTabla(self):
        self.tableView.setRowCount(0)
        if not self.model: #si no esta establecido el modelo no hago nada
            return

        data = self.model.select().dicts()
        if self.condicion:
            for c in self.condicion:
                data = data.where(c)

        if self.lineEditBusqueda.text():
            if self.ordenBusqueda:
                data = data.where(self.ordenBusqueda.contains(self.lineEditBusqueda.text()))
            else:
                Ventanas.showAlert("Sistema", "Orden no establecido y no se puede realizar la busqueda")

        data = data.limit(self.limite)
        for d in data:
            if self.camposAMostrar:
                item = [d[x.column_name] for x in self.camposAMostrar]
            else:
                item = [d[x] for x in d]
            self.tableView.AgregaItem(item)

    def ArmaDatos(self):
        self.verticalLayoutDatos = QVBoxLayout(self.tabDetalle)
        self.verticalLayoutDatos.setObjectName("verticalLayoutDatos")
        self.ArmaCarga()
        fila = 0

        self.grdBotones = QGridLayout()
        self.grdBotones.setObjectName("grdBotones")
        self.btnAceptar = Boton(self.tabDetalle, imagen="imagenes/guardar.png", tamanio=QSize(32,32))
        self.btnAceptar.setObjectName("btnAceptar")
        self.grdBotones.addWidget(self.btnAceptar, 0, 0, 1, 1)

        self.btnCancelar = Boton(self.tabDetalle, imagen="imagenes/log-out.png", tamanio=QSize(32,32))
        self.btnCancelar.setObjectName("btnCancelar")
        self.grdBotones.addWidget(self.btnCancelar, 0, 1, 1, 1)
        self.verticalLayoutDatos.addLayout(self.grdBotones)
        self.verticalLayout.addWidget(self.tabWidget)
        self.btnCancelar.clicked.connect(self.btnCancelarClicked)
        self.btnAceptar.clicked.connect(self.btnAceptarClicked)
        self.verticalLayoutDatos.addStretch(1)

    def Busqueda(self):
        self.ArmaTabla()

    def ConectaWidgets(self):
        self.lineEditBusqueda.textChanged.connect(self.Busqueda)
        self.btnCerrar.clicked.connect(self.cerrarformulario)
        self.btnBorrar.clicked.connect(self.Borrar)
        self.btnEditar.clicked.connect(self.Modifica)
        self.btnAgregar.clicked.connect(self.Agrega)

    @inicializar_y_capturar_excepciones
    def Borrar(self, *args, **kwargs):
        if not self.tableView.currentRow() != -1:
            return

        if not self.campoClave:
            Ventanas.showAlert("Sistema", "No tenes establecido el campo clave y no podemos continuar")

        id = self.tableView.ObtenerItem(fila=self.tableView.currentRow(), col=self.campoClave.column_name.capitalize())
        data = self.model.get_by_id(id)
        data.delete_instance()
        self.ArmaTabla()

    def Modifica(self):

        self.tipo = 'M'
        if not self.tableView.currentRow() != -1:
            return

        if not self.campoClave:
            Ventanas.showAlert("Sistema", "No tenes establecido el campo clave y no podemos continuar")

        id = self.tableView.ObtenerItem(fila=self.tableView.currentRow(), col=self.campoClave.column_name.capitalize())
        print(self.tableView.currentRow(), id)
        data = self.model.select().where(self.campoClave == int(id)).dicts()
        self.tabDetalle.setEnabled(True)
        self.tabWidget.setCurrentIndex(1)
        self.CargaDatos(data)

    def CargaDatos(self, data=None):
        if not data:
            return
        for d in data:
            for k in d:
                if k in self.controles:
                    if k == self.campoClave.column_name:
                        self.controles[k].setEnabled(False)
                    if isinstance(self.controles[k], QLineEdit):
                        if isinstance(d[k], (int, decimal.Decimal)):
                            self.controles[k].setText(str(d[k]))
                        else:
                            self.controles[k].setText(d[k])
                    elif isinstance(self.controles[k], (QCheckBox, CheckBox)):
                        if EsVerdadero(d[k]) or d[k]:
                            self.controles[k].setChecked(True)
                        else:
                            self.controles[k].setChecked(False)
                    elif isinstance(self.controles[k], QComboBox):
                        if isinstance(d[k], (bytes,)):
                            if EsVerdadero(self.cursor[k]):
                                self.controles[k].setCurrentIndex(self.controles[k].findData('Si'))
                            else:
                                self.controles[k].setCurrentIndex(self.controles[k].findData('No'))
                        else:
                            self.controles[k].setCurrentIndex(self.controles[k].findData(d[k]))
                    self.controles[k].setStyleSheet("background-color: white")

    def ArmaEntrada(self, nombre="", boxlayout=None, texto='', *args, **kwargs):
        if not boxlayout:
            boxlayout = QHBoxLayout()
            lAgrega = True
        else:
            lAgrega = False

        if not texto:
            texto = nombre.capitalize()

        labelNombre = Etiqueta(texto=texto)
        labelNombre.setObjectName("labelNombre")
        boxlayout.addWidget(labelNombre)

        if 'control' in kwargs:
            lineEditNombre = kwargs['control']
        else:
            lineEditNombre = EntradaTexto()

        if 'relleno' in kwargs:
            lineEditNombre.relleno = kwargs['relleno']

        if 'inputmask' in kwargs:
            lineEditNombre.setInputMask(kwargs['inputmask'])

        lineEditNombre.setObjectName(nombre)
        boxlayout.addWidget(lineEditNombre)
        if 'enabled' in kwargs:
            lineEditNombre.setEnabled(kwargs['enabled'])

        self.controles[nombre] = lineEditNombre

        if lAgrega:
            self.verticalLayoutDatos.addLayout(boxlayout)
        return boxlayout

    def btnCancelarClicked(self):
        self.tabWidget.setCurrentIndex(0)
        self.tabDetalle.setEnabled(False)

    def btnAceptarClicked(self):
        # data = self.model.get_by_id(self.controles[self.campoClave.column_name].text())
        # data.nombre = self.controles['nombre'].text()
        self.ArmaTabla()
        self.btnCancelarClicked()

    def ArmaCarga(self):
        pass

    def Agrega(self):
        for x in self.controles:
            self.controles[x].setText('')
            self.controles[x].setStyleSheet("background-color: white")
        self.tabDetalle.setEnabled(True)
        self.tabWidget.setCurrentIndex(1)