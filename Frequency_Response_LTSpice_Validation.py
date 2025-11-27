# ==============================================================================
# PROJECT: FINAL RLC FILTER VALIDATION SCRIPT
# DESCRIPTION: Final script with all fixes, now utilizing two subplots 
#              (Analytical vs. Simulation) to ensure maximum visibility 
#              of both data types.
# ==============================================================================

import sympy
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import subprocess
import os
import warnings
# Try to import ltspice package
try:
    import ltspice 
except ImportError:
    pass 

# --- 1. CONFIGURATION & IMPORTS ---

warnings.filterwarnings("ignore", category=UserWarning) 

# CRITICAL FIX: The working path for your LTSpice executable
LTSPICE_PATH = r"C:\Users\Kris\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
# Reading the single node voltage V(Nout) 
NODE_OUT = "V(Nout)" 

# --- Circuit Configuration (Python uses these values for analytical model) ---
L_val = 10e-3 # 10 mH
C_val = 10e-9 # 10 nF

# Three scenarios varying R to change the Quality Factor (Q)
SCENARIOS = [
    {'R': 1.0, 'label': 'High Q', 'color': 'red', 'linestyle': '-'},
    {'R': 10.0, 'label': 'Medium Q', 'color': 'blue', 'linestyle': '--'},
    {'R': 100.0, 'label': 'Low Q', 'color': 'green', 'linestyle': ':'}
]

# --- LTSpice Raw Reader Setup ---
LTSpice_READER_AVAILABLE = False 
try:
    import ltspice 
    class LTSpiceRawRead:
        def __init__(self, filename):
            self.reader = ltspice.Ltspice(filename)
            self.reader.parse()

        def get_frequency(self):
            return self.reader.get_frequency()
            
        def get_data(self, expression):
            return self.reader.get_data(expression)

    LTSpice_READER_AVAILABLE = True 

except ImportError:
    LTSpice_READER_AVAILABLE = False


# ==============================================================================
# 2. SYMBOLIC ANALYSIS & HELPER FUNCTIONS
# ==============================================================================

s, t, R, L, C = sympy.symbols('s t R L C', positive=True)
H_s = R / (R + s * L + 1 / (s * C))
H_s_simplified = H_s.simplify()
num_expr, den_expr = sympy.fraction(H_s_simplified)

num_coeffs_symbolic = num_expr.as_poly(s).all_coeffs()
den_coeffs_symbolic = den_expr.as_poly(s).all_coeffs()

w0_rad = np.sqrt(1 / (L_val * C_val))
f0_hz = w0_rad / (2 * np.pi)


def create_netlist_file(resistance_val, output_path):
    """
    Creates the netlist using LTSpice standard unit prefixes (10m, 10n) 
    and the high-resolution AC sweep.
    """
    L_netlist_val = "10m"
    C_netlist_val = "10n"
    
    netlist_content = f"""
* RLC Bandpass Filter Netlist (Vout measured at V(Nout))
V1 Nin 0 AC 1
L1 Nin N1 {L_netlist_val}
C1 N1 Nout {C_netlist_val} 
R1 Nout 0 {resistance_val} ; Vout is measured across R1
.save V(Nout) ; Force LTSpice to save this node's voltage
.ac dec 1000 1 1Meg ; FIX: Sweep with 1000 points/decade for high-Q peak
.end
"""
    with open(output_path, 'w') as f:
        f.write(netlist_content)
    
    return True

def run_ltspice_ac_sim(netlist_file):
    """Executes the LTSpice simulation in batch mode."""
    raw_file = netlist_file.replace(".net", ".raw")
    
    if not os.path.exists(LTSPICE_PATH):
        raise FileNotFoundError(f"LTSpice executable not found at: {LTSPICE_PATH}")
        
    command = [
        LTSPICE_PATH,
        "-b",               
        netlist_file        
    ]
    
    print(f"-> Running LTSpice simulation for {netlist_file}...")
    
    # Run the LTSpice simulation
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    return raw_file

def get_ltspice_bode_data(raw_file, voltage_expression=NODE_OUT):
    """
    Reads the complex voltage V(Nout) directly from the raw file and 
    returns the magnitude normalized to its peak (0 dB).
    """
    if not LTSpice_READER_AVAILABLE or not os.path.exists(raw_file):
        print(f"-> WARNING: Raw file {raw_file} not found or reader is disabled. Skipping plot.")
        return None, None
        
    try:
        raw_data = ltspice.Ltspice(raw_file)
        raw_data.parse()
        
        V_complex = raw_data.get_data(voltage_expression)

        if V_complex is None or len(V_complex) == 0:
             print(f"-> ERROR: Voltage expression {voltage_expression} found no data in raw file.")
             return None, None
        
        # FIX: Assume get_frequency() returns frequency in Hz
        freq_hz = raw_data.get_frequency() 
        
        # Calculate raw magnitude in dB
        magnitude_db_raw = 20 * np.log10(np.abs(V_complex))
        
        # FIX: Normalize the simulation magnitude so its peak is 0 dB
        max_mag_db = np.max(magnitude_db_raw)
        magnitude_db_normalized = magnitude_db_raw - max_mag_db
        
        return freq_hz, magnitude_db_normalized
        
    except Exception as e:
        print(f"-> ERROR reading {raw_file} data: {e}")
        return None, None


# ==============================================================================
# 4. PLOTTING AND VALIDATION LOOP
# ==============================================================================

if not LTSpice_READER_AVAILABLE:
    print("\n--- LTSpice validation skipped due to missing Python library. ---")

# CRITICAL FIX: Create two subplots sharing the X-axis
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 10))
fig.suptitle(f'Bandpass Filter Validation (f₀: {f0_hz/1e3:.2f} kHz)', fontsize=16)

# Store data for plotting
analytical_plots = []
sim_plots = []

print(f"\n--- Starting RLC Filter Analysis ---")
print(f"Center Frequency f₀: {f0_hz/1e3:.2f} kHz")

for i, scenario in enumerate(SCENARIOS):
    R_val = scenario['R']
    netlist_name = f"bandpass_R_{R_val:.1f}.net"
    
    # --- AUTOMATION STEP 1 & 2: CREATE NETLIST and RUN LTSpice ---
    if create_netlist_file(R_val, netlist_name):
        try:
            raw_file = run_ltspice_ac_sim(netlist_name)
        except Exception as e:
            print(f"-> FATAL ERROR during simulation run: {e}. Skipping LTSpice plot.")
            continue
            
    
    # --- ANALYTICAL STEP: Calculate Scipy System ---
    num_coeffs = [float(c.subs({R: R_val, L: L_val, C: C_val})) for c in num_coeffs_symbolic]
    den_coeffs = [float(c.subs({R: R_val, L: L_val, C: C_val})) for c in den_coeffs_symbolic]
    
    sys = signal.lti(num_coeffs, den_coeffs)
    
    f_start = 1.0  # 1 Hz
    f_end = 1e6    # 1 MHz
    w_vector = 2 * np.pi * np.logspace(np.log10(f_start), np.log10(f_end), 5000)
    
    w, mag, phase = signal.bode(sys, w=w_vector) 
    f_laplace = w / (2 * np.pi)
    
    Q_analytic = w0_rad / (R_val / L_val)
    print(f"R={R_val:.1f}Ω: Analytical Q={Q_analytic:.1f}")
    
    # Store analytical data
    analytical_plots.append({
        'f': f_laplace,
        'mag': mag,
        'color': scenario['color'],
        'linestyle': scenario['linestyle'],
        'label': f"R={R_val:.1f}Ω (Q={Q_analytic:.1f})"
    })

    # --- VALIDATION STEP: Read and Store LTSpice Data ---
    if LTSpice_READER_AVAILABLE:
        raw_file = netlist_name.replace(".net", ".raw") 
        f_sim, mag_sim = get_ltspice_bode_data(raw_file)
        
        if f_sim is not None:
            # Store simulation data
            sim_plots.append({
                'f': f_sim,
                'mag': mag_sim,
                'color': scenario['color'],
                'label': f"R={R_val:.1f}Ω (Q={Q_analytic:.1f})"
            })

# --- Plotting Analytical Curves on Top Axis (ax1) ---
for plot_data in analytical_plots:
    ax1.semilogx(plot_data['f'], plot_data['mag'], 
                 color=plot_data['color'], 
                 linestyle=plot_data['linestyle'],
                 linewidth=2.5, 
                 label=plot_data['label'])

ax1.set_title('Analytical Laplace Transfer Function', fontsize=12)
ax1.set_ylabel('Magnitude (dB)', fontsize=12)
ax1.axvline(f0_hz, color='gray', linestyle='-.')
ax1.grid(True, which="both", ls="-", alpha=0.5)
ax1.legend(fontsize=9, loc='lower left')

# --- Plotting Simulation Data on Bottom Axis (ax2) ---
for plot_data in sim_plots:
    ax2.semilogx(plot_data['f'], plot_data['mag'], 
                 marker='.',      
                 markersize=4, 
                 linestyle='None', 
                 color=plot_data['color'], 
                 label=plot_data['label'])
                 
ax2.set_title('LTSpice Simulation Data (Normalized Peak)', fontsize=12)
ax2.set_xlabel('Frequency (Hz)', fontsize=12)
ax2.set_ylabel('Magnitude (dB)', fontsize=12)
ax2.axvline(f0_hz, color='gray', linestyle='-.', label=f'Center Frequency $f_0$ ({f0_hz/1e3:.2f} kHz)')
ax2.grid(True, which="both", ls="-", alpha=0.5)
ax2.legend(fontsize=9, loc='lower left')


# --- Final Plot Customization (Shared Limits) ---
# Ensure both Y-axes have the same scale
ax1.set_ylim(-100, 5) 
ax2.set_ylim(-100, 5) 

# Ensure both X-axes have the same scale
ax1.set_xlim(10**0, 10**6) 

plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to fit suptitle

# Save the figure to a file
plt.savefig('RLC_Bandpass_Validation_Split.png')
print("\nPlot successfully saved to: RLC_Bandpass_Validation_Split.png")

# Optional: Attempt to show the plot interactively
plt.show() 

# ==============================================================================
# END OF SCRIPT
# ==============================================================================