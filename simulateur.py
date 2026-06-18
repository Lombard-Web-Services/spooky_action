#!/usr/bin/env python3
"""
simulateur.py - Simulateur numérique pour le framework de linguistique quantique
Équations de Lindblad - Version corrigée
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import pandas as pd

def run_simulation():
    """Exécute la simulation du protocole de fermeture"""
    
    print("=" * 60)
    print("🔬 SIMULATION DU PROTOCOLE DE FERMETURE")
    print("=" * 60)
    print()
    
    # Constantes
    HBAR = 1.0
    GAMMA = 0.5
    OMEGA_SYL = 2 * np.pi * 0.8
    OMEGA_THETA = 2 * np.pi * 6.0
    
    # État initial
    psi0 = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    rho0 = np.outer(psi0, psi0.conj())
    
    print(f"📐 Dimension de l'espace de Hilbert : {rho0.shape[0]}")
    print(f"   État initial : |ψ⟩ = (|00⟩ + |11⟩)/√2")
    print()
    
    # Opérateurs Pauli
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    I = np.eye(2, dtype=complex)
    
    # Opérateurs de Lindblad
    a_syl = (sigma_x + 1j * sigma_y) / np.sqrt(2)
    L1 = np.sqrt(5 * GAMMA) * np.kron(a_syl, I)
    L2_1 = np.sqrt(2 * GAMMA) * np.kron(sigma_z, I)
    L2_2 = np.sqrt(2 * GAMMA) * np.kron(I, sigma_z)
    k_state = np.zeros((4, 4), dtype=complex)
    k_state[0, 1] = 1.0
    L3 = np.sqrt(3 * GAMMA) * k_state
    L4 = np.sqrt(1.5 * GAMMA) * np.kron(sigma_z, sigma_z)
    L_list = [L1, L2_1, L2_2, L3, L4]
    
    def lindblad_superoperator(rho):
        result = np.zeros_like(rho, dtype=complex)
        for L in L_list:
            L_dag = L.conj().T
            result += L @ rho @ L_dag - 0.5 * (L_dag @ L @ rho + rho @ L_dag @ L)
        return result
    
    def hamiltonian_close(t):
        delta = np.random.rand(2) * 2 * np.pi
        phi_sum = sum(np.sin(3 * OMEGA_THETA * t + delta[p]) for p in range(2))
        H1 = -1.5 * OMEGA_SYL * np.kron(sigma_z, I)
        H2 = 0.8 * OMEGA_SYL * phi_sum * np.kron(I, sigma_z)
        H3 = -0.5 * OMEGA_SYL * np.kron(sigma_x, sigma_x)
        return H1 + H2 + H3
    
    def dydt(t, y):
        rho = y.reshape(4, 4)
        H = hamiltonian_close(t)
        drho = -1j * (H @ rho - rho @ H) / HBAR
        drho += lindblad_superoperator(rho)
        return drho.flatten()
    
    # Simulation
    t_span = (0, 30)
    print("⏳ Résolution des équations de Lindblad...")
    
    try:
        sol = solve_ivp(dydt, t_span, rho0.flatten(), method='RK45', rtol=1e-6, atol=1e-8, max_step=0.1)
        print(f"✅ Simulation terminée : {len(sol.t)} points")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return
    
    # Extraction des résultats
    coherence = []
    population = []
    entropy = []
    
    for y in sol.y.T:
        rho = y.reshape(4, 4)
        # Cohérence
        off_diag = sum(np.abs(rho[i, j])**2 for i in range(4) for j in range(4) if i != j)
        coherence.append(np.sqrt(off_diag))
        # Population |normal⟩
        population.append(np.real(rho[0, 0]))
        # Entropie
        eigvals = np.linalg.eigvalsh(rho)
        eigvals = eigvals[eigvals > 1e-12]
        entropy.append(-np.sum(eigvals * np.log(eigvals + 1e-12)))
    
    # Affichage
    print("\n📊 RÉSULTATS :")
    print(f"  Cohérence maximale : {max(coherence):.4f}")
    print(f"  Cohérence finale : {coherence[-1]:.4f}")
    print(f"  Population |normal⟩ finale : {population[-1]*100:.2f}%")
    print(f"  Entropie maximale : {max(entropy):.4f} bits")
    print()
    
    # Graphique
    print("📈 Génération du graphique...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    axes[0, 0].plot(sol.t, coherence, 'b-', linewidth=2)
    axes[0, 0].set_xlabel('Temps (s)')
    axes[0, 0].set_ylabel('Cohérence c(t)')
    axes[0, 0].set_title('Évolution de la cohérence')
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].plot(sol.t, population, 'g-', linewidth=2)
    axes[0, 1].axhline(y=0.95, color='r', linestyle='--', label='Seuil 95%')
    axes[0, 1].axhline(y=0.99, color='orange', linestyle='--', label='Seuil 99%')
    axes[0, 1].set_xlabel('Temps (s)')
    axes[0, 1].set_ylabel('Population |normal⟩')
    axes[0, 1].set_title("Population de l'état normal")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].plot(sol.t, entropy, 'r-', linewidth=2)
    axes[1, 0].set_xlabel('Temps (s)')
    axes[1, 0].set_ylabel('Entropie S(t) (bits)')
    axes[1, 0].set_title("Évolution de l'entropie")
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].plot(coherence, population, 'purple', linewidth=2)
    axes[1, 1].set_xlabel('Cohérence c(t)')
    axes[1, 1].set_ylabel('Population |normal⟩')
    axes[1, 1].set_title('Espace des phases')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('simulation_fermeture.png', dpi=150)
    print("✅ Graphique sauvegardé : simulation_fermeture.png")
    
    # Sauvegarde des données
    df = pd.DataFrame({
        'Temps (s)': sol.t,
        'Cohérence': coherence,
        'Population |normal⟩': population,
        'Entropie': entropy
    })
    df.to_csv('simulation_donnees.csv', index=False)
    print("✅ Données sauvegardées : simulation_donnees.csv")
    print("\n✅ Simulation terminée avec succès !")
    
    return sol, coherence, population, entropy

if __name__ == "__main__":
    np.random.seed(42)
    run_simulation()
