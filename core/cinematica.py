import numpy as np
from scipy.integrate import solve_ivp
import math

class MotorFisico:
    def __init__(self):
        self.g = 9.81 # Gravedad local controlada

    def simular_caida(self, ms, r, rho_f, eta, t_max=5.0, fps=60):
        Vs = (4/3) * math.pi * (r**3)
        b = 6 * math.pi * eta * r
        
        def sistema_edo(t, Y):
            y, v = Y
            dy_dt = v
            dv_dt = self.g - (rho_f * Vs * self.g) / ms - (b / ms) * v
            return [dy_dt, dv_dt]

        t_eval = np.linspace(0, t_max, int(t_max * fps))
        sol = solve_ivp(sistema_edo, [0, t_max], [0.0, 0.0], t_eval=t_eval, method='RK45')
        return t_eval, sol.y[0]

    def simular_vaciado(self, tapa_cerrada, rho, h_inicial=1.0, A_valvula=0.05, t_max=15.0, fps=60):
        A_tanque = 1.0 
        P_atm = 101325.0 
        volumen_aire_inicial = 0.5 * A_tanque 
        
        def edo_vaciado(t, h):
            if h[0] <= 0.01: return [0.0] 
            
            presion_superficie = P_atm
            if tapa_cerrada:
                volumen_aire_actual = volumen_aire_inicial + (h_inicial - h[0]) * A_tanque
                presion_superficie = P_atm * ((volumen_aire_inicial / volumen_aire_actual)**0.3)
            
            delta_P = presion_superficie - P_atm
            energia_interna = self.g * h[0] + (delta_P / rho)
            
            if energia_interna <= 0: return [0.0] 
                
            v_salida = math.sqrt(2 * energia_interna)
            dh_dt = - (A_valvula / A_tanque) * v_salida
            return [dh_dt]

        t_eval = np.linspace(0, t_max, int(t_max * fps))
        sol = solve_ivp(edo_vaciado, [0, t_max], [h_inicial], t_eval=t_eval, method='RK45')
        return t_eval, sol.y[0]