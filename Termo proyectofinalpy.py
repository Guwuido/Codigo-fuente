import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue

class SimuladorCalentamientoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Curva de Calentamiento del Agua")
        self.root.geometry("1400x900")
        
        self.result_queue = queue.Queue()
        
        self.resultados = None
        self.simulacion_activa = False
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_frame = ttk.Frame(main_frame, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_input_section(left_frame)
        self.setup_results_section(left_frame)
        self.setup_graphs_section(right_frame)
    
    def setup_input_section(self, parent):
        # Titulo
        title_label = ttk.Label(parent, text="SIMULADOR DE CALENTAMIENTO DEL AGUA", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame para inputs
        input_frame = ttk.LabelFrame(parent, text="Parámetros de Simulación", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Temperatura inicial
        ttk.Label(input_frame, text="Temperatura inicial (°C):").pack(anchor=tk.W)
        self.temp_inicial_var = tk.StringVar(value="20")
        ttk.Entry(input_frame, textvariable=self.temp_inicial_var).pack(fill=tk.X, pady=(0, 10))
        
        # Masa total
        ttk.Label(input_frame, text="Masa total del agua (kg):").pack(anchor=tk.W)
        self.masa_var = tk.StringVar(value="1.0")
        ttk.Entry(input_frame, textvariable=self.masa_var).pack(fill=tk.X, pady=(0, 10))
        
        # Potencia
        ttk.Label(input_frame, text="Potencia de la parrilla (W):").pack(anchor=tk.W)
        self.potencia_var = tk.StringVar(value="2000")
        ttk.Entry(input_frame, textvariable=self.potencia_var).pack(fill=tk.X, pady=(0, 10))
        
        # Presion
        ttk.Label(input_frame, text="Presión atmosférica (kPa):").pack(anchor=tk.W)
        self.presion_var = tk.StringVar(value="101.325")
        ttk.Entry(input_frame, textvariable=self.presion_var).pack(fill=tk.X, pady=(0, 10))
        
        # Checkbox para mostrar tablas detalladas
        self.mostrar_tablas_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(input_frame, text="Mostrar tablas segundo a segundo", 
                       variable=self.mostrar_tablas_var).pack(anchor=tk.W, pady=(5, 10))
        
        self.simular_btn = ttk.Button(input_frame, text="Iniciar Simulación", 
                                     command=self.iniciar_simulacion)
        self.simular_btn.pack(fill=tk.X, pady=(10, 0))
        
        self.progress = ttk.Progressbar(input_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
    
    def setup_results_section(self, parent):
        results_frame = ttk.LabelFrame(parent, text="Resultados y Estado", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, width=40)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        status_frame = ttk.Frame(results_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Listo para simular", 
                                     foreground="green")
        self.status_label.pack()
    
    def setup_graphs_section(self, parent):
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.fig.suptitle('Simulación de Calentamiento del Agua', fontsize=14, fontweight='bold')
        
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = self.fig.add_subplot(2, 2, 3)
        self.ax4 = self.fig.add_subplot(2, 2, 4)
        
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = tk.Frame(parent)
        toolbar.pack(fill=tk.X)
        
        self.init_empty_graphs()
    
    def init_empty_graphs(self):
        self.ax1.set_title('Temperatura vs Tiempo')
        self.ax1.set_xlabel('Tiempo (minutos)')
        self.ax1.set_ylabel('Temperatura (°C)')
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.set_title('Masa Sólida vs Tiempo')
        self.ax2.set_xlabel('Tiempo (minutos)')
        self.ax2.set_ylabel('Masa (kg)')
        self.ax2.grid(True, alpha=0.3)
        
        self.ax3.set_title('Masa Líquida vs Tiempo')
        self.ax3.set_xlabel('Tiempo (minutos)')
        self.ax3.set_ylabel('Masa (kg)')
        self.ax3.grid(True, alpha=0.3)
        
        self.ax4.set_title('Todas las Fases vs Tiempo')
        self.ax4.set_xlabel('Tiempo (minutos)')
        self.ax4.set_ylabel('Masa (kg)')
        self.ax4.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def log_message(self, message):
        """Añade un mensaje al área de resultados"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message, color="black"):
        """Actualiza el mensaje de estado"""
        self.status_label.config(text=message, foreground=color)
        self.root.update_idletasks()
    
    def imprimir_tablas_detalladas(self, tiempos, temperaturas, masas_solidas, masas_liquidas, masas_vapor):
        """Imprime las tablas segundo a segundo"""
        self.log_message("\n" + "="*80)
        self.log_message("TABLAS DETALLADAS SEGUNDO A SEGUNDO")
        self.log_message("="*80)
        
        # Tabla 1: Temperatura del sistema en función del tiempo
        self.log_message("\n📊 TABLA 1: TEMPERATURA DEL SISTEMA EN FUNCIÓN DEL TIEMPO")
        self.log_message("-" * 60)
        self.log_message(f"{'Tiempo (s)':<12} {'Tiempo (min)':<15} {'Temperatura (°C)':<18}")
        self.log_message("-" * 60)
        
        # Mostrar cada segundo hasta los primeros 60 segundos, luego cada 30 segundos
        for i, tiempo in enumerate(tiempos):
            if tiempo <= 60 or tiempo % 30 == 0 or i == len(tiempos) - 1:
                minutos = tiempo / 60
                temp = temperaturas[i]
                self.log_message(f"{tiempo:<12.0f} {minutos:<15.2f} {temp:<18.2f}")
        
        # Tabla 2: Masa de agua en fase sólida en función del tiempo
        self.log_message("\n📊 TABLA 2: MASA DE AGUA EN FASE SÓLIDA EN FUNCIÓN DEL TIEMPO")
        self.log_message("-" * 60)
        self.log_message(f"{'Tiempo (s)':<12} {'Tiempo (min)':<15} {'Masa Sólida (kg)':<18}")
        self.log_message("-" * 60)
        
        for i, tiempo in enumerate(tiempos):
            if tiempo <= 60 or tiempo % 30 == 0 or i == len(tiempos) - 1:
                minutos = tiempo / 60
                masa_sol = masas_solidas[i]
                self.log_message(f"{tiempo:<12.0f} {minutos:<15.2f} {masa_sol:<18.6f}")
        
        # Tabla 3: Masa de agua en fase líquida en función del tiempo
        self.log_message("\n📊 TABLA 3: MASA DE AGUA EN FASE LÍQUIDA EN FUNCIÓN DEL TIEMPO")
        self.log_message("-" * 60)
        self.log_message(f"{'Tiempo (s)':<12} {'Tiempo (min)':<15} {'Masa Líquida (kg)':<18}")
        self.log_message("-" * 60)
        
        for i, tiempo in enumerate(tiempos):
            if tiempo <= 60 or tiempo % 30 == 0 or i == len(tiempos) - 1:
                minutos = tiempo / 60
                masa_liq = masas_liquidas[i]
                self.log_message(f"{tiempo:<12.0f} {minutos:<15.2f} {masa_liq:<18.6f}")
        
        # Tabla 4: Masa de agua en fase vapor en función del tiempo
        self.log_message("\n📊 TABLA 4: MASA DE AGUA EN FASE VAPOR EN FUNCIÓN DEL TIEMPO")
        self.log_message("-" * 60)
        self.log_message(f"{'Tiempo (s)':<12} {'Tiempo (min)':<15} {'Masa Vapor (kg)':<18}")
        self.log_message("-" * 60)
        
        for i, tiempo in enumerate(tiempos):
            if tiempo <= 60 or tiempo % 30 == 0 or i == len(tiempos) - 1:
                minutos = tiempo / 60
                masa_vap = masas_vapor[i]
                self.log_message(f"{tiempo:<12.0f} {minutos:<15.2f} {masa_vap:<18.6f}")
        
        # Tabla combinada: Todas las fases
        self.log_message("\n📊 TABLA COMBINADA: TODAS LAS FASES EN FUNCIÓN DEL TIEMPO")
        self.log_message("-" * 90)
        self.log_message(f"{'Tiempo':<8} {'Temp':<8} {'M.Sólida':<10} {'M.Líquida':<11} {'M.Vapor':<10} {'Total':<8}")
        self.log_message(f"{'(s)':<8} {'(°C)':<8} {'(kg)':<10} {'(kg)':<11} {'(kg)':<10} {'(kg)':<8}")
        self.log_message("-" * 90)
        
        for i, tiempo in enumerate(tiempos):
            if tiempo <= 60 or tiempo % 30 == 0 or i == len(tiempos) - 1:
                temp = temperaturas[i]
                masa_sol = masas_solidas[i]
                masa_liq = masas_liquidas[i]
                masa_vap = masas_vapor[i]
                total = masa_sol + masa_liq + masa_vap
                
                self.log_message(f"{tiempo:<8.0f} {temp:<8.2f} {masa_sol:<10.6f} {masa_liq:<11.6f} {masa_vap:<10.6f} {total:<8.6f}")
        
        self.log_message("\n" + "="*80)
        self.log_message("FIN DE TABLAS DETALLADAS")
        self.log_message("="*80)
    
    def iniciar_simulacion(self):
        if self.simulacion_activa:
            return
        
        try:
            temp_inicial = float(self.temp_inicial_var.get())
            masa_total = float(self.masa_var.get())
            potencia = float(self.potencia_var.get())
            presion_kpa = float(self.presion_var.get())
            
            if masa_total <= 0 or potencia <= 0 or presion_kpa <= 0:
                self.log_message("Error: Los valores de masa, potencia y presión deben ser positivos.")
                return
            
            if temp_inicial < -273.15:
                self.log_message("Error: La temperatura no puede ser menor al cero absoluto (-273.15°C).")
                return
            
            self.results_text.delete(1.0, tk.END)
            
            self.simular_btn.config(state='disabled')
            self.progress.start()
            self.simulacion_activa = True
            self.update_status("Simulando...", "orange")
            
            thread = threading.Thread(target=self.ejecutar_simulacion,
                                    args=(temp_inicial, masa_total, potencia, presion_kpa))
            thread.daemon = True
            thread.start()
            
            self.root.after(100, self.check_simulation_complete)
            
        except ValueError:
            self.log_message("Error: Por favor ingrese valores numéricos válidos.")
            self.update_status("Error en parámetros", "red")
    
    def ejecutar_simulacion(self, temp_inicial, masa_total, potencia, presion_kpa):
        """Ejecuta la simulación en un thread separado"""
        try:
            resultados = self.simular_calentamiento(temp_inicial, masa_total, potencia, presion_kpa)
            self.result_queue.put(('success', resultados))
        except Exception as e:
            self.result_queue.put(('error', str(e)))
    
    def check_simulation_complete(self):
        """Verifica si la simulación ha terminado"""
        try:
            result_type, result_data = self.result_queue.get_nowait()
            
            self.progress.stop()
            self.simular_btn.config(state='normal')
            self.simulacion_activa = False
            
            if result_type == 'success':
                self.resultados = result_data
                self.update_graphs()
                self.update_status("Simulación completada", "green")
            else:
                self.log_message(f"Error durante la simulación: {result_data}")
                self.update_status("Error en simulación", "red")
                
        except queue.Empty:
            self.root.after(100, self.check_simulation_complete)
    
    def update_graphs(self):
        """Actualiza las gráficas con los resultados"""
        if not self.resultados:
            return
        
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        
        tiempos_min = [t/60 for t in self.resultados['tiempo']]
        temp_saturacion = self.resultados.get('temp_saturacion', 100)
        
        self.ax1.plot(tiempos_min, self.resultados['temperatura'], 'r-', linewidth=2)
        self.ax1.axhline(y=0, color='b', linestyle='--', alpha=0.7, label='Punto de fusión')
        self.ax1.axhline(y=temp_saturacion, color='g', linestyle='--', alpha=0.7, 
                        label=f'Punto de ebullición ({temp_saturacion:.1f}°C)')
        self.ax1.set_xlabel('Tiempo (minutos)')
        self.ax1.set_ylabel('Temperatura (°C)')
        self.ax1.set_title('Temperatura vs Tiempo')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend()
        
        self.ax2.plot(tiempos_min, self.resultados['masa_solida'], 'b-', linewidth=2, label='Masa sólida')
        self.ax2.set_xlabel('Tiempo (minutos)')
        self.ax2.set_ylabel('Masa (kg)')
        self.ax2.set_title('Masa Sólida vs Tiempo')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.legend()
        
        self.ax3.plot(tiempos_min, self.resultados['masa_liquida'], 'g-', linewidth=2, label='Masa líquida')
        self.ax3.set_xlabel('Tiempo (minutos)')
        self.ax3.set_ylabel('Masa (kg)')
        self.ax3.set_title('Masa Líquida vs Tiempo')
        self.ax3.grid(True, alpha=0.3)
        self.ax3.legend()
        
        self.ax4.plot(tiempos_min, self.resultados['masa_solida'], 'b-', linewidth=2, label='Sólida')
        self.ax4.plot(tiempos_min, self.resultados['masa_liquida'], 'g-', linewidth=2, label='Líquida')
        self.ax4.plot(tiempos_min, self.resultados['masa_vapor'], 'r-', linewidth=2, label='Vapor')
        self.ax4.set_xlabel('Tiempo (minutos)')
        self.ax4.set_ylabel('Masa (kg)')
        self.ax4.set_title('Todas las Fases vs Tiempo')
        self.ax4.grid(True, alpha=0.3)
        self.ax4.legend()
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    # Constantes
CS = 2100.0       # J/kg°C (hielo)
CL = 4186.0       # J/kg°C (agua líquida)
LF = 333000.0     # J/kg (fusión)
PSTAR = 1.0       # MPa
TSTAR = 1.0       # K

# Constantes del modelo de saturación
n = [None,
     0.11670521452767e4,
     -0.72421316703206e6,
     -0.17073846940092e2,
     0.12020824702470e5,
     -0.32325550322333e7,
     0.14915108613530e2,
     -0.48232657361591e4,
     0.40511340542057e6,
     -0.23855557567849,
     0.65017534844798e3]


def calc_saturation_temperature(p_kpa: float) -> float:
    beta = (p_kpa / 1000.0 / PSTAR) ** 0.25
    E = beta ** 2 + n[3] * beta + n[6]
    F = n[1] * beta ** 2 + n[4] * beta + n[7]
    G = n[2] * beta ** 2 + n[5] * beta + n[8]
    D = (2 * G) / (-F - math.sqrt(F ** 2 - 4 * E * G))
    T_s = TSTAR * (
        n[10] + D - math.sqrt((n[10] + D) ** 2 - 4 * (n[9] + n[10] * D))
    ) / 2
    return T_s


def latent_heat_vaporization(T_s_c: float) -> float:
    return (
        2256.4 / ((T_s_c + 273.15) / 647.0969) ** (1 - 0.57665623)
    ) * 1000.0


def run_simulation(
    T0_c: float,
    mass_kg: float,
    power_w: float,
    pressure_kpa: float,
    dt: float = 1.0,
) -> Tuple[List[Tuple[float, float, float, float, float, float]], float]:
    Ts_c = calc_saturation_temperature(pressure_kpa) - 273.15
    h_vap = latent_heat_vaporization(Ts_c)

    Q1 = mass_kg * CS * abs(min(T0_c, 0.0))
    Q2 = mass_kg * LF if T0_c < 0 else 0.0
    start_T_liquid = 0.0 if T0_c < 0 else T0_c
    Q3 = mass_kg * CL * max(Ts_c - start_T_liquid, 0.0)
    Q4 = mass_kg * h_vap

    t = 0.0
    Q = 0.0
    T = T0_c
    solid = mass_kg if T0_c < 0 else 0.0
    liquid = mass_kg - solid
    gas = 0.0

    history: List[Tuple[float, float, float, float, float, float]] = []

    while gas < mass_kg:
        history.append((t, Q, T, solid, liquid, gas))
        Q += power_w * dt
        t += dt
        if T0_c < 0 and Q < Q1:  # calentamiento de hielo
            T = T0_c + Q / (mass_kg * CS)
        elif T0_c < 0 and Q < Q1 + Q2:  # fusión
            T = 0.0
            frac = (Q - Q1) / Q2
            solid = mass_kg * (1 - frac)
            liquid = mass_kg * frac
        elif Q < Q1 + Q2 + Q3:  # calentamiento del agua
            T = start_T_liquid + (Q - Q1 - Q2) / (mass_kg * CL)
            solid = 0.0
            liquid = mass_kg
        elif Q < Q1 + Q2 + Q3 + Q4:  # vaporización
            T = Ts_c
            solid = 0.0
            liquid = mass_kg - mass_kg * (Q - Q1 - Q2 - Q3) / Q4
            gas = mass_kg * (Q - Q1 - Q2 - Q3) / Q4
        else:
            T = Ts_c
            solid = 0.0
            liquid = 0.0
            gas = mass_kg

    history.append((t, Q, T, solid, liquid, gas))
    return history, Ts_c


# ==== EJECUCIÓN PRINCIPAL ====
if __name__ == "__main__":
    try:
        T0 = float(input("Temperatura inicial (°C): "))
        m = float(input("Masa de agua (kg): "))
        P = float(input("Potencia suministrada (W): "))
        p = float(input("Presión atmosférica (kPa): "))
    except Exception as exc:
        print("Entrada inválida:", exc)
        raise SystemExit(1)

    data, Ts = run_simulation(T0, m, P, p)

    print(f"\nTemperatura de saturación calculada: {Ts:.2f} °C\n")
    print("t(s), Q(J), T(°C), masa_sólida(kg), masa_líquida(kg), masa_vapor(kg)")
    for row in data:
        print("{:.0f}, {:.1f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}".format(*row))

    # Guardar como CSV
    with open("simulacion_agua.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Tiempo (s)", "Energía (J)", "Temperatura (°C)", "Masa sólida (kg)", "Masa líquida (kg)", "Masa vapor (kg)"])
        writer.writerows(data)

def main():
    root = tk.Tk()
    app = SimuladorCalentamientoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()