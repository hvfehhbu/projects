import cmath
import math

def parallel(z1, z2):
    return (z1 * z2) / (z1 + z2)

print("--- Solving Problem 28 ---")

# Circuit Parameters
R1 = 40
R2 = 40
L2 = 4
C = 5e-3 # 5000 uF
R3 = 10
L3 = 1

# --- Step 1: DC Component (omega = 0) ---
print("\n--- Step 1: DC Component ---")
# Sources
E_branch1 = 20
E_branch2_dc = 10

# Impedances (L short, C open)
# Branch 1: R1 + Source
# Branch 2: R2 + Source (L2 short)
# Branch 3: Open (C open) -> Admittance = 0
# Branch 4: R3 (L3 short)

# Nodal Analysis at Node A (Ref B)
# Sigma ( (V_A - V_source) / R ) = 0
# (U_dc - E_branch1)/R1 + (U_dc - E_branch2_dc)/R2 + U_dc/R3 = 0
# U_dc * (1/R1 + 1/R2 + 1/R3) = E_branch1/R1 + E_branch2_dc/R2

G1 = 1/R1
G2 = 1/R2
G3 = 0 # Open
G4 = 1/R3

Sigma_G = G1 + G2 + G4
Sigma_I = (E_branch1 * G1) + (E_branch2_dc * G2)

U_dc = Sigma_I / Sigma_G
print(f"U_dc = {U_dc:.4f} V")


# --- Step 2: AC Component 1 (omega = 10) ---
print("\n--- Step 2: AC Component 1 (w=10) ---")
w1 = 10
# Source: 60 sin(10t + 45) = 60 cos(10t + 45 - 90) = 60 cos(10t - 45)
# Phasor: 60 angle -45
mag1 = 60
phase1_deg = -45
E_ac1 = cmath.rect(mag1, math.radians(phase1_deg))
print(f"Source E_ac1: {E_ac1:.4f} (Polar: {mag1}<{phase1_deg})")

# Impedances
Z1 = R1 # Source E (DC) is shorted -> just R1
Z2 = R2 + 1j * w1 * L2
Z3 = 1 / (1j * w1 * C)
Z4 = R3 + 1j * w1 * L3

print(f"Z1: {Z1}")
print(f"Z2: {Z2}")
print(f"Z3: {Z3}")
print(f"Z4: {Z4}")

# Admittances
Y1 = 1/Z1
Y2 = 1/Z2
Y3 = 1/Z3
Y4 = 1/Z4

# Nodal Analysis
# U_ac1 * (Y1 + Y2 + Y3 + Y4) = (Source_Branch2 / Z2) ? No, Source is IN Branch 2
# Branch 2 current source equivalent: E_ac1 / Z2
# Wait, direction?
# User said "Nguồn áp... mắc nối tiếp".
# Assuming positive terminal up for E_ac1 (same as E).
# Current injection into Node A = E_ac1 / Z2
# U_ac1 * Sigma_Y = E_ac1 * Y2

Sigma_Y_1 = Y1 + Y2 + Y3 + Y4
I_source_1 = E_ac1 * Y2

U_ac1 = I_source_1 / Sigma_Y_1
mag_u1, phase_u1 = cmath.polar(U_ac1)
phase_u1_deg = math.degrees(phase_u1)
print(f"U_ac1: {U_ac1:.4f} (Polar: {mag_u1:.4f}<{phase_u1_deg:.4f})")


# --- Step 3: AC Component 2 (omega = 20) ---
print("\n--- Step 3: AC Component 2 (w=20) ---")
w2 = 20
# Source: 20 sqrt(2) cos(20t)
# Phasor: 20 sqrt(2) angle 0
mag2 = 20 * math.sqrt(2)
phase2_deg = 0
E_ac2 = cmath.rect(mag2, math.radians(phase2_deg))
print(f"Source E_ac2: {E_ac2:.4f} (Polar: {mag2:.4f}<{phase2_deg})")

# Impedances
Z1_2 = R1
Z2_2 = R2 + 1j * w2 * L2
Z3_2 = 1 / (1j * w2 * C)
Z4_2 = R3 + 1j * w2 * L3

print(f"Z1: {Z1_2}")
print(f"Z2: {Z2_2}")
print(f"Z3: {Z3_2}")
print(f"Z4: {Z4_2}")

# Admittances
Y1_2 = 1/Z1_2
Y2_2 = 1/Z2_2
Y3_2 = 1/Z3_2
Y4_2 = 1/Z4_2

# Nodal Analysis
# U_ac2 * Sigma_Y = E_ac2 * Y2_2
Sigma_Y_2 = Y1_2 + Y2_2 + Y3_2 + Y4_2
I_source_2 = E_ac2 * Y2_2

U_ac2 = I_source_2 / Sigma_Y_2
mag_u2, phase_u2 = cmath.polar(U_ac2)
phase_u2_deg = math.degrees(phase_u2)
print(f"U_ac2: {U_ac2:.4f} (Polar: {mag_u2:.4f}<{phase_u2_deg:.4f})")

print("\n--- Final Expression ---")
print(f"u(t) = {U_dc:.2f} + {mag_u1:.2f}cos(10t + {phase_u1_deg:.2f}deg) + {mag_u2:.2f}cos(20t + {phase_u2_deg:.2f}deg)")
