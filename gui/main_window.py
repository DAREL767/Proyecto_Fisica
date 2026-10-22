from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame, QSlider
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from simulation.renderer import PhysicsRenderer
import pyqtgraph as pg
from pyqtgraph import TextItem
from core.cinematica import MotorFisico # Importamos el núcleo matemático
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFrame, QSlider, QDoubleSpinBox, QCheckBox, QComboBox, QTabWidget, QSizePolicy

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FluidSim Lab v1.0")
        self.resize(1200, 720) 
        
        # --- CREACIÓN DE PESTAÑAS ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab { background: #1E293B; color: white; padding: 12px 20px; font-weight: bold; border-top-left-radius: 4px; border-top-right-radius: 4px;}
            QTabBar::tab:selected { background: #3B82F6; }
        """)
        self.setCentralWidget(self.tabs)

        # ==========================================
        # PESTAÑA 1: RENDERIZADO DE SIMULACIÓN
        # ==========================================
        self.tab_sim = QWidget()
        main_layout = QHBoxLayout(self.tab_sim)
        
        # 1. Panel de Controles (Izquierda)
        control_panel = QFrame()
        control_panel.setObjectName("controlPanel")
        control_panel.setFixedWidth(350)
        control_layout = QVBoxLayout(control_panel)
        
        title_label = QLabel("PARÁMETROS DEL EXPERIMENTO")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(title_label)
        
        self.spin_ms = self.crear_control_parametro(control_layout, "Masa del cuerpo (kg):", 0.01, 10.0, 0.25)
        self.spin_r = self.crear_control_parametro(control_layout, "Radio de la esfera (m):", 0.01, 0.2, 0.04)
        self.spin_rho = self.crear_control_parametro(control_layout, "Densidad del fluido (kg/m³):", 100, 8000.0, 1000.0) 
        self.spin_eta = self.crear_control_parametro(control_layout, "Viscosidad dinámica (Pa·s):", 0.01, 1.5, 0.15)
        
        self.spin_h = self.crear_control_parametro(control_layout, "Nivel inicial del tanque (1.0 = Lleno):", 0.1, 1.0, 1.0)
        # Sincronización en tiempo real del nivel
        self.spin_h.valueChanged.connect(lambda val: [setattr(self.canvas, 'porcentaje_llenado', val), self.canvas.update()])
        
        self.check_tapa = QCheckBox("Sistema Cerrado (Sin presión atmosférica P_atm)")
        self.check_tapa.setStyleSheet("color: #F8FAFC; font-weight: bold; margin-top: 5px;")
        control_layout.addWidget(self.check_tapa)

        self.combo_fluidos = QComboBox()
        self.combo_fluidos.addItems(["Personalizado / Manual", "Agua (1000 kg/m³, 0.001 Pa·s)", 
                                     "Aceite de Motor (850 kg/m³, 0.2 Pa·s)", 
                                     "Glicerina (1260 kg/m³, 1.4 Pa·s)", "Miel (1420 kg/m³, 10.0 Pa·s)"])
        self.combo_fluidos.setStyleSheet("background-color: #F8FAFC; color: #0F172A; padding: 5px; border-radius: 4px;")
        self.combo_fluidos.currentIndexChanged.connect(self.cambiar_fluido)
        control_layout.addWidget(QLabel("Preajustes de Fluido:"))
        control_layout.addWidget(self.combo_fluidos)
        
        self.spin_valvula = self.crear_control_parametro(control_layout, "Área de la válvula (m²):", 0.01, 0.2, 0.05)
        
        # Botones
        self.btn_valvula = QPushButton("💧 ABRIR VÁLVULA")
        self.btn_valvula.setMinimumHeight(40) 
        self.btn_valvula.setStyleSheet("background-color: #3B82F6; color: white; font-weight: bold; font-size: 14px;")
        self.btn_valvula.clicked.connect(self.ejecutar_vaciado)
        control_layout.addWidget(self.btn_valvula)

        btn_start = QPushButton("▶ INICIAR SIMULACIÓN")
        btn_start.setObjectName("startBtn")
        btn_start.clicked.connect(self.ejecutar_experimento)
        control_layout.addWidget(btn_start)
        
        btn_pause = QPushButton("⏸ PAUSAR / REANUDAR")
        btn_pause.clicked.connect(self.toggle_pausa)
        control_layout.addWidget(btn_pause)

        # Añadimos espacio elástico al final
        control_layout.addStretch()

        # 2. Lienzo de Física (Derecha) - ¡AQUÍ SE CREA EL LAYOUT ANTES DEL LETRERO!
        simulation_panel = QFrame()
        simulation_layout = QVBoxLayout(simulation_panel)
        
        canvas_title = QLabel("ÁREA DE SIMULACIÓN (PHYSICS RENDER)")
        canvas_title.setObjectName("canvasTitle")
        canvas_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_title.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        simulation_layout.addWidget(canvas_title)
        
        self.canvas = PhysicsRenderer()
        simulation_layout.addWidget(self.canvas)
        
        btn_export = QPushButton("🎥 EXPORTAR MP4 (TRACKER)")
        btn_export.setObjectName("exportBtn")
        btn_export.clicked.connect(lambda: self.canvas.generar_video_tracker())
        simulation_layout.addWidget(btn_export)
        
        main_layout.addWidget(control_panel)
        main_layout.addWidget(simulation_panel)

        # ==========================================
        # PESTAÑA 2: ANÁLISIS MATEMÁTICO
        # ==========================================
        self.tab_analisis = QWidget()
        analisis_layout = QVBoxLayout(self.tab_analisis)
        
        pg.setConfigOption('background', '#1E293B')
        pg.setConfigOption('foreground', '#F8FAFC')
        
        self.grafica = pg.PlotWidget(title="Cinemática: Posición vs Tiempo")
        self.grafica.setLabel('left', 'Desplazamiento / Llenado')
        self.grafica.setLabel('bottom', 'Tiempo', units='s')
        self.grafica.showGrid(x=True, y=True, alpha=0.3)
        self.curva_grafica = self.grafica.plot([], [], pen=pg.mkPen(color='#10B981', width=3), fillLevel=0, fillBrush=(16, 185, 129, 40))
        
        from pyqtgraph import TextItem
        self.rastreador_texto = TextItem(text="", color='#F8FAFC', anchor=(0, 1))
        self.grafica.addItem(self.rastreador_texto)
        
        analisis_layout.addWidget(self.grafica)

        # Añadir las pestañas al widget principal
        self.tabs.addTab(self.tab_sim, "⚙️ Renderizado Físico")
        self.tabs.addTab(self.tab_analisis, "📈 Análisis Matemático")

    def crear_control_parametro(self, layout, label_text, min_val, max_val, default_val):
        label = QLabel(label_text)
        layout.addWidget(label)
        
        h_layout = QHBoxLayout()
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(int(min_val * 100))
        slider.setMaximum(int(max_val * 100))
        slider.setValue(int(default_val * 100))
        
        spinbox = QDoubleSpinBox()
        # Flexibilidad total: El usuario puede teclear números enormes si lo desea
        spinbox.setRange(0.001, 99999.0) 
        spinbox.setValue(default_val)
        spinbox.setDecimals(3)
        
        # Sincronización
        slider.valueChanged.connect(lambda val: spinbox.setValue(val / 100.0))
        
        h_layout.addWidget(slider)
        h_layout.addWidget(spinbox)
        layout.addLayout(h_layout)
        layout.addSpacing(10)
        
        return spinbox

    def toggle_pausa(self):
        # Activa o desactiva el temporizador de la animación en curso
        if self.canvas.timer.isActive():
            self.canvas.timer.stop()
        elif self.canvas.frame_actual < len(self.canvas.posiciones_matematicas):
            self.canvas.timer.start(16)

    def ejecutar_experimento(self):
        ms = self.spin_ms.value()
        r = self.spin_r.value()
        rho = self.spin_rho.value()
        eta = self.spin_eta.value()
        
        # Restaura los textos de la gráfica para la caída libre
        self.grafica.setTitle("Cinemática: Desplazamiento vs Tiempo")
        self.grafica.setLabel('left', 'Desplazamiento', units='m')
        self.curva_grafica.setData([], [])
        
        self.canvas.porcentaje_llenado = self.spin_h.value()
        
        motor = MotorFisico()
        tiempos, posiciones = motor.simular_caida(ms, r, rho, eta)
        # Pasamos también el rastreador al renderizador
        self.canvas.iniciar_animacion(tiempos, posiciones, self.curva_grafica, self.rastreador_texto)

    def cambiar_fluido(self, index):
        if index == 1: # Agua
            self.spin_rho.setValue(1000.0)
            self.spin_eta.setValue(0.001)
        elif index == 2: # Aceite
            self.spin_rho.setValue(850.0)
            self.spin_eta.setValue(0.2)
        elif index == 3: # Glicerina
            self.spin_rho.setValue(1260.0)
            self.spin_eta.setValue(1.4)
        elif index == 4: # Miel
            self.spin_rho.setValue(1420.0)
            self.spin_eta.setValue(10.0)

    def ejecutar_vaciado(self):
        tapa_cerrada = self.check_tapa.isChecked()
        rho = self.spin_rho.value()
        h_inicial = self.spin_h.value() 
        area_valvula = self.spin_valvula.value()
        
        self.grafica.setTitle("Hidrodinámica: Nivel del Agua vs Tiempo")
        self.grafica.setLabel('left', 'Nivel de Llenado', units='%')
        self.curva_grafica.setData([], []) 
        
        motor = MotorFisico()
        tiempos, alturas = motor.simular_vaciado(tapa_cerrada, rho, h_inicial, area_valvula) 
        self.canvas.iniciar_vaciado(tiempos, alturas, self.curva_grafica, self.rastreador_texto)
