import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Cargar y aplicar los estilos QSS
    try:
        with open("gui/styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Advertencia: No se encontró el archivo styles.qss")
        
    window = MainWindow()
    window.show()
    
    # Iniciar el bucle de la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()