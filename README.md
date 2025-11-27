# 🚀 Laplace Transform Analysis & Validation: RLC Bandpass Filter Tuning (UK English)

A detailed project write-up demonstrating the power of the **Laplace transform** in simplifying complex circuit analysis and providing immediate intuition for filter design. This validation rigorously couples the analytical (mathematical) solution with Python numerical analysis and confirms the results against professional circuit simulation (LTSpice).

## 💡 The Core Intuition: From Calculus to Algebra

The fundamental purpose of this exercise is to demonstrate the practical utility of the Laplace transform in electrical engineering.

Analysing this second-order RLC circuit in the **Time Domain** would require solving a **second-order differential equation** (calculus). The **Laplace Transform** converts this complex problem into a simple **algebraic equation** in the $s$-domain: the **Transfer Function $H(s)$**.

This algebraic form instantly reveals the key parameters that define the circuit's behaviour: the **Centre Frequency ($\omega_0$)** and the **Quality Factor ($Q$)**. 

[Image of Laplace transform formula on a circuit diagram]


---

## 🔌 Circuit and Analysis Overview

| Feature | Details |
| :--- | :--- |
| **Circuit** | Series RLC Circuit (Output voltage $V_R$ measured across the resistor)  |
| **Analysis** | Frequency Response (Bode Plot) |
| **Domain** | $s$-domain (Laplace) $\rightarrow$ $j\omega$-domain (Frequency) |
| **Tools** | **Python** (`SymPy`, `SciPy`, `Matplotlib`), **LTSpice** |
| **Fixed Components** | $L = 10 \text{ mH}$, $C = 10 \text{ nF}$ |
| **Fixed Centre Frequency ($f_0$)** | $15.92 \text{ kHz}$ |

---

## 🔬 Analytical Derivation and Key Parameters

The **Transfer Function**, $H(s) = \frac{V_R(s)}{V_{in}(s)}$, is derived using the voltage divider rule and component impedances ($Z_R=R$, $Z_L=sL$, $Z_C=1/sC$):

$$H(s) = \frac{Z_R}{Z_R + Z_L + Z_C} = \frac{R}{R + sL + \frac{1}{sC}}$$

Simplifying this algebraic expression yields the standard second-order form:

$$H(s) = \frac{(\frac{R}{L})s}{s^2 + (\frac{R}{L})s + \frac{1}{LC}}$$

From this algebraic $H(s)$, we algebraically extract the circuit's key design parameters:

| Parameter | Formula | Dependence | Insight |
| :--- | :--- | :--- | :--- |
| **Centre Frequency ($\omega_0$)** | $\omega_0 = \sqrt{1/LC}$ | $L, C$ only | Constant for all scenarios |
| **Bandwidth ($BW$)** | $BW = R/L$ | $R, L$ | Directly proportional to $R$ |
| **Quality Factor ($Q$)** | $Q = \omega_0 / BW = \frac{1}{R} \sqrt{\frac{L}{C}}$ | $R, L, C$ | Inversely proportional to $R$ |

---

## 💻 Python Implementation and Scenario Testing

The Python programme performs the automated validation:

1.  **Symbolic Manipulation:** It employs **SymPy** to define $H(s)$ and extract the polynomial coefficients for the numerator and denominator.
2.  **Numerical Analysis:** It uses **SciPy's `signal.lti`** module to convert the $s$-domain coefficients into a system object, which then calculates the smooth, theoretical frequency response (Bode plot) for the **Laplace model**.
3.  **LTSpice Automation:** It executes the LTSpice simulator in batch mode (`-b`) for each scenario, generating raw simulation data.
4.  **Data Processing:** It employs the `ltspice` library to read the raw files, applying necessary corrections (frequency unit conversion, peak normalization), and preparing the data for plotting.

### Core Scenarios Tested

The programme varies $R$ to demonstrate the effect on the **Quality Factor ($Q$)** while holding $f_0$ constant:

| Scenario | Resistance ($R$) | Calculated $Q$ | Resulting Bandwidth ($BW$) | Filter Selectivity |
| :---: | :---: | :---: | :---: | :--- |
| **1** | $1.0 \, \Omega$ | $1000.0$ | $15.9 \text{ Hz}$ | **High $Q$ (Sharp, Highly Selective)** |
| **2** | $10.0 \, \Omega$ | $100.0$ | $159.2 \text{ Hz}$ | **Medium $Q$ (Balanced)** |
| **3** | $100.0 \, \Omega$ | $10.0$ | $1.59 \text{ kHz}$ | **Low $Q$ (Broad, Less Selective)** |

---

## 📈 Validation Success and Debugging Summary

The final visualisation, split into two subplots with identical scales, shows an **excellent match** between the Laplace model (smooth lines) and the LTSpice simulation (data markers), confirming the validity of the analytical framework.

### Critical Debugging & Resolution Steps:

| Issue | Observation | Cause | Resolution Implemented |
| :--- | :--- | :--- | :--- |
| **Frequency Shift** | LTSpice peak at $\sim 2.5 \text{ kHz}$ (Expected: $15.92 \text{ kHz}$) | Mismatch factor of $\approx 2\pi$. The Python code was erroneously dividing the frequency by $2\pi$, as the raw file reader already outputted data in **Hertz**. | **Removed the $2\pi$ division** when reading LTSpice frequency data. |
| **High-Q Vertical Offset** | The $1\Omega$ (High-Q) curve was slightly offset vertically. | The filter peak ($BW \approx 16 \text{ Hz}$) was too narrow for the default AC sweep resolution (`dec 100`) to capture the true maximum gain. | **Increased AC sweep resolution** in netlist to `dec 1000` (1000 points/decade) to accurately capture the peak. |
| **Plot Visibility** | Dense LTSpice markers obscured the smooth Laplace lines. | Overlapping data series in a single plot. | **Implemented two separate subplots** with shared log-scale X-axes and identical Y-axes limits to ensure both data types are clearly visible. |

---

## ⚙️ How to Run

### Prerequisites

You will require the following Python libraries installed, in addition to the LTSpice software itself:

```bash
pip install sympy numpy scipy matplotlib ltspice
Note: You must ensure the LTSPICE_PATH variable within the Python programme is correctly set to the path of your LTSpice executable (e.g., r"C:\Users\Kris\AppData\Local\Programs\ADI\LTspice\LTspice.exe").

Execution
Save the complete Python code as Frequency_Response_Validation.py.

Execute the programme from your terminal:

Bash

python Frequency_Response_Validation.py
This will automatically run all LTSpice simulations, process the raw data, calculate the analytical curves, and save the final figure to RLC_Bandpass_Validation_Split.png.
