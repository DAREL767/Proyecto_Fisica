import cv2
import math
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QImage, QPainterPath
from PyQt6.QtCore import Qt, QTimer

class PhysicsRenderer(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #0F172A; border-radius: 8px;")
        
        self.radio_visual = 25
        self.esfera_y = -100 
        self.esfera_y_anterior = -100 # Para calcular la velocidad visual
        self.y_inicial_fisica = 0

        self.tiempo_actual_visual = 0.0
        self.posiciones_matematicas = []
        self.tiempos_matematicos = []
        self.frame_actual = 0
        self.escala_pixeles = 200 
        self.porcentaje_llenado = 1.0 
        self.modo_animacion = "caida" 
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)
        
    def iniciar_animacion(self, tiempos, posiciones_y, curva_grafica, rastreador_texto):
        self.modo_animacion = "caida"
        self.tiempos_matematicos = tiempos
        self.posiciones_matematicas = posiciones_y
        self.curva_grafica = curva_grafica
        self.historial_t = []
        self.historial_y = []
        self.frame_actual = 0
        self.esfera_y_anterior = self.y_inicial_fisica
        self.rastreador_texto = rastreador_texto
        self.timer.start(16)

    def iniciar_vaciado(self, tiempos, posiciones_y, curva_grafica, rastreador_texto):
        self.modo_animacion = "vaciado"
        self.tiempos_matematicos = tiempos
        self.posiciones_matematicas = posiciones_y
        self.curva_grafica = curva_grafica
        self.historial_t = []
        self.historial_y = []
        self.frame_actual = 0
        self.rastreador_texto = rastreador_texto
        self.timer.start(16)

    def actualizar_frame(self):
        if self.frame_actual < len(self.posiciones_matematicas):
            valor_actual = self.posiciones_matematicas[self.frame_actual]
            tiempo_actual = self.tiempos_matematicos[self.frame_actual]
            
            # --- CORRECCIÓN: Actualizamos el tiempo visual para la línea roja ---
            self.tiempo_actual_visual = tiempo_actual
            
            self.historial_t.append(tiempo_actual)
            self.historial_y.append(valor_actual)
            self.curva_grafica.setData(self.historial_t, self.historial_y)

            self.rastreador_texto.setPos(tiempo_actual, valor_actual)
            self.rastreador_texto.setText(f"t: {tiempo_actual:.2f} s | f(t): {valor_actual:.3f}")
            
            if self.modo_animacion == "caida":
                self.esfera_y_anterior = self.esfera_y 
                nueva_y = self.y_inicial_fisica + (valor_actual * self.escala_pixeles)
                limite_fondo = self.height() - self.radio_visual
                
                if nueva_y >= limite_fondo:
                    self.esfera_y = limite_fondo
                    self.timer.stop() 
                elif nueva_y <= self.y_inicial_fisica and valor_actual < 0:
                    self.esfera_y = self.y_inicial_fisica - (self.radio_visual / 2) 
                    self.timer.stop() 
                else:
                    self.esfera_y = nueva_y
                    
            elif self.modo_animacion == "vaciado":
                self.porcentaje_llenado = valor_actual
                
            self.frame_actual += 1
            self.update() 
        else:
            self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        margen_inferior = 30
        tope_tanque = int(self.height() * 0.3)
        espacio_agua = (self.height() - margen_inferior) - tope_tanque
        nivel_base = (self.height() - margen_inferior) - (espacio_agua * self.porcentaje_llenado)
        
        desplazamiento_y = 0
        if self.modo_animacion == "caida" and self.esfera_y + self.radio_visual > nivel_base:
            desplazamiento_y = 12 
        self.y_inicial_fisica = nivel_base - desplazamiento_y

        # 1. Fluido Dinámico con Ondas (Aspecto orgánico)
        path_agua = QPainterPath()
        path_agua.moveTo(0, int(self.y_inicial_fisica))
        
        if self.modo_animacion == "caida" and self.timer.isActive() and desplazamiento_y > 0:
            # Crea ondas sinusoidales en la superficie
            for x in range(0, self.width(), 10):
                y_onda = self.y_inicial_fisica + math.sin(x * 0.05 + self.frame_actual * 0.2) * 4
                path_agua.lineTo(x, int(y_onda))
        else:
            path_agua.lineTo(self.width(), int(self.y_inicial_fisica))
            
        path_agua.lineTo(self.width(), self.height() - margen_inferior)
        path_agua.lineTo(0, self.height() - margen_inferior)
        
        painter.setBrush(QBrush(QColor(59, 130, 246, 180)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path_agua)

        # 2. Vara de calibración 1.00 m
        pen_vara = QPen(QColor(248, 250, 252))
        pen_vara.setWidth(3)
        painter.setPen(pen_vara)
        x_vara = 50
        y_fin_vara = tope_tanque + self.escala_pixeles 
        painter.drawLine(x_vara, tope_tanque, x_vara, y_fin_vara)
        painter.drawLine(x_vara - 5, tope_tanque, x_vara + 5, tope_tanque)
        painter.drawLine(x_vara - 5, y_fin_vara, x_vara + 5, y_fin_vara)
        painter.drawText(x_vara + 15, int((tope_tanque + y_fin_vara) / 2), "1.00 m")

        # 3. Válvula y Chorro Parabólico
        ancho_valvula = 30
        alto_valvula = 15
        x_valvula = self.width() - ancho_valvula
        y_valvula = self.height() - margen_inferior - alto_valvula
        painter.setBrush(QBrush(QColor(15, 23, 42))) 
        painter.drawRect(x_valvula, y_valvula, ancho_valvula, alto_valvula)

        if self.modo_animacion == "vaciado" and self.timer.isActive() and self.porcentaje_llenado > 0.01:
            path_chorro = QPainterPath()
            path_chorro.moveTo(x_valvula, y_valvula + alto_valvula)
            alcance_x = -60 * self.porcentaje_llenado # El agua cae en curva hacia la izquierda
            
            # Curva de Bezier para simular parábola
            path_chorro.quadTo(x_valvula + alcance_x, y_valvula + alto_valvula + 15, 
                               x_valvula + alcance_x, self.height())
            path_chorro.lineTo(x_valvula + alcance_x + 15, self.height())
            path_chorro.quadTo(x_valvula + alcance_x + 15, y_valvula + alto_valvula + 15, 
                               x_valvula + ancho_valvula, y_valvula + alto_valvula)
                               
            painter.setBrush(QBrush(QColor(59, 130, 246, 200)))
            painter.drawPath(path_chorro)

        # 4. Esfera, Estela y Línea de Tiempo
        if self.modo_animacion == "caida":
            x_esfera = int(self.width() / 2 - self.radio_visual)
            centro_y_esfera = int(self.esfera_y)
            
            velocidad_visual = centro_y_esfera - self.esfera_y_anterior
            if velocidad_visual > 0 and centro_y_esfera > self.y_inicial_fisica:
                painter.setBrush(QBrush(QColor(255, 255, 255, 40))) 
                painter.drawEllipse(x_esfera + 5, int(centro_y_esfera - velocidad_visual*2), 
                                    self.radio_visual*2 - 10, self.radio_visual*2 + int(velocidad_visual*3))

            painter.setBrush(QBrush(QColor(16, 185, 129)))
            painter.setPen(QPen(QColor(248, 250, 252), 2))
            painter.drawEllipse(x_esfera, centro_y_esfera - self.radio_visual, self.radio_visual * 2, self.radio_visual * 2)

            # LÍNEA DE TIEMPO VERTICAL (Se congela al pausar)
            pen_tiempo = QPen(QColor(239, 68, 68, 200)) # Rojo tecnológico
            pen_tiempo.setWidth(2)
            pen_tiempo.setStyle(Qt.PenStyle.DotLine)
            painter.setPen(pen_tiempo)
            
            x_tiempo = x_esfera + self.radio_visual * 2 + 15
            y_tope_linea = max(tope_tanque, centro_y_esfera - 80)
            painter.drawLine(x_tiempo, centro_y_esfera, x_tiempo, y_tope_linea)
            
            painter.setPen(QPen(QColor(248, 250, 252)))
            painter.drawText(x_tiempo + 5, y_tope_linea + 10, f"t = {self.tiempo_actual_visual:.2f} s")

            if centro_y_esfera >= self.y_inicial_fisica:
                pen_marcador = QPen(QColor(16, 185, 129, 150))
                pen_marcador.setWidth(2)
                pen_marcador.setStyle(Qt.PenStyle.DashLine)
                painter.setPen(pen_marcador)
                painter.drawLine(x_vara, centro_y_esfera, x_esfera, centro_y_esfera)
                
                profundidad_metros = (centro_y_esfera - self.y_inicial_fisica) / self.escala_pixeles
                painter.setPen(QPen(QColor(248, 250, 252)))
                painter.drawText(x_vara + 65, centro_y_esfera - 5, f"{profundidad_metros:.2f} m")

    def generar_video_tracker(self, ruta_archivo="exportacion_tracker.mp4"):
        if len(self.posiciones_matematicas) == 0:
            print("No hay datos para exportar. Ejecuta una simulación primero.")
            return

        print("Renderizando video para Tracker a 60 FPS, por favor espera...")
        frame_original = self.frame_actual
        esfera_y_original = self.esfera_y
        
        pixmap_prueba = self.grab()
        img_prueba = pixmap_prueba.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        ancho_real = img_prueba.width()
        alto_real = img_prueba.height()
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(ruta_archivo, fourcc, 60.0, (ancho_real, alto_real))
        
        for i, desplazamiento_metros in enumerate(self.posiciones_matematicas):
            self.frame_actual = i
            
            # Replicamos la lógica estricta para la exportación sin estelas para no confundir a Tracker
            if self.modo_animacion == "caida":
                nueva_y = self.y_inicial_fisica + (desplazamiento_metros * self.escala_pixeles)
                limite_fondo = self.height() - self.radio_visual
                if nueva_y >= limite_fondo:
                    self.esfera_y = limite_fondo
                elif nueva_y <= self.y_inicial_fisica and desplazamiento_metros < 0:
                    self.esfera_y = self.y_inicial_fisica - (self.radio_visual / 2) 
                else:
                    self.esfera_y = nueva_y
                    
            elif self.modo_animacion == "vaciado":
                self.porcentaje_llenado = desplazamiento_metros
                
            pixmap = self.grab()
            img = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
            
            ptr = img.bits()
            ptr.setsize(alto_real * ancho_real * 4)
            arr = np.array(ptr).reshape((alto_real, ancho_real, 4))
            arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            out.write(arr_bgr)
            
        out.release() 
        self.frame_actual = frame_original
        self.esfera_y = esfera_y_original
        print(f"¡Éxito absoluto! Video guardado como: {ruta_archivo}")