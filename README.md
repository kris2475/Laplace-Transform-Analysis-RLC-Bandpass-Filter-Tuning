# 🚀 Laplace Transform Analysis: RLC Bandpass Filter Tuning

A Python project demonstrating the power of the **Laplace transform** in simplifying complex circuit analysis and providing immediate intuition for filter design. This repository couples analytical (mathematical) solutions with numerical plotting (Python) and validates the results against professional circuit simulation (LTSpice).

## 💡 The Core Intuition

The primary goal of this project is to show *why* engineers use the Laplace transform.

The analysis of a second-order circuit in the time domain requires solving a **second-order differential equation** (calculus). The Laplace transform converts this problem into a simple **algebraic equation** in the $s$-domain: the **Transfer Function $H(s)$**.

This algebraic form instantly reveals the key parameters that define the circuit's behavior: the **Center Frequency ($\omega_0$)** and the **Quality Factor ($Q$)**.

---

## 🔌 Circuit and Analysis Overview

| Feature | Details |
| :--- | :--- |
| **Circuit** | Series RLC Circuit (Output voltage $V_R$ taken across the resistor)  |
| **Analysis** | Frequency Response (Bode Plot) |
| **Domain** | $s$-domain (Laplace) $\rightarrow$ $j\omega$-domain (Frequency) |
| **Tools** | **Python** (`SymPy`, `SciPy`, `Matplotlib`), **LTSpice** |

---

## 🔬 Analytical Derivation

The analysis begins by defining the impedance of each component in the $s$-domain:

* Resistor Impedance: $Z_R = R$
* Inductor Impedance: $Z_L = sL$
* Capacitor Impedance: $Z_C = 1/sC$

The **Transfer Function**, $H(s) = \frac{V_R(s)}{V_{in}(s)}$, is derived using the voltage divider rule:

$$H(s) = \frac{Z_R}{Z_R + Z_L + Z_C} = \frac{R}{R + sL + \frac{1}{sC}}$$

Simplifying this algebraic expression yields the standard form that reveals the circuit's characteristics:

$$H(s) = \frac{(\frac{R}{L})s}{s^2 + (\frac{R}{L})s + \frac{1}{LC}}$$

From this $H(s)$, we can algebraically identify the circuit's key parameters:

* **Center Frequency ($\omega_0$):** $\omega_0 = \sqrt{1/LC}$
* **Bandwidth ($BW$):** $BW = R/L$
* **Quality Factor ($Q$):** $Q = \omega_0 / BW = \frac{1}{R} \sqrt{\frac{L}{C}}$

---

## 💻 Python Implementation

The Python script (`Frequency_Response.py`) performs three core tasks:

1.  **Symbolic Manipulation:** Uses **SymPy** to define $H(s)$ and automatically extract the polynomial coefficients for the numerator and denominator.
2.  **Numerical Analysis:** Uses **SciPy's `signal.lti`** module to convert the $s$-domain coefficients into a system object, and then calculates the frequency response (Bode plot) by substituting $s=j\omega$.
3.  **Visualization:** Uses **Matplotlib** to plot the response for different scenarios, highlighting how simple changes in $R$ affect the **Quality Factor ($Q$)**.

### Core Scenarios Tested

To demonstrate the decoupled control offered by $H(s)$, the script uses fixed $L$ and $C$ values to maintain a constant **Center Frequency** ($f_0 \approx 160$ kHz) while varying **$R$** to change the **$Q$ factor**:

| Scenario | Resistance ($R$) | Quality Factor ($Q$) | Resulting Filter |
| :---: | :---: | :---: | :--- |
| **1** | $1.0 \, \Omega$ | High | **Sharp, highly selective** |
| **2** | $10.0 \, \Omega$ | Medium | Balanced selectivity |
| **3** | $100.0 \, \Omega$ | Low | **Broad, less selective** |

---

## 📈 Results and Validation

### Analytical Plot (Python Output)

The generated plot showcases the direct relationship between the Resistance ($R$) and the filter's sharpness ($Q$).

* Notice that the **peak frequency** remains the same for all three curves, proving $f_0$ is independent of $R$.
* As $R$ increases (from $1\Omega$ to $100\Omega$), the peak becomes **wider and shorter** (the $Q$ factor decreases). 

### LTSpice Validation

The final step for the project is to run an **AC Analysis** in LTSpice using the exact same component values for $R, L, C$ and overlay the simulation data onto the analytical plot. This confirms that the results derived from the **simple algebraic Laplace model** are accurate representations of the physical circuit behavior.

---

## ⚙️ How to Run

### Prerequisites

You need the following Python libraries installed:

```bash
pip install sympy numpy scipy matplotlib
Execution
Save the provided Python code as Frequency_Response.py.

Run the script:

Bash

python Frequency_Response.py
(Optional) Perform an AC sweep in LTSpice for the three resistor values and integrate the data using a raw file reader library (e.g., lts_reader) to complete the validation step.
