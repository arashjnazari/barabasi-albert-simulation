import random
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def custom_barabasi_albert(N, m):
    """
    Generate a scale-free network using Barabasi-Albert model from scratch.
    پیاده‌سازی مدل باراباشی-آلبرت برای ساخت شبکه از صفر
    """
    # گام اول: گراف اولیه با m + 1 گره
    G = nx.complete_graph(m + 1)
    
    # گام دوم: رشد گام‌به‌گام و اتصال ترجیحی
    for new_node in range(m + 1, N):
        nodes = list(G.nodes())
        degrees = [G.degree(n) for n in nodes]
        total_degree = sum(degrees)
        
        # احتمال اتصال: P_i = k_i / sum(k)
        probabilities = [d / total_degree for d in degrees]
        
        # انتخاب m گره غیرتکراری بر اساس وزن درجه
        selected_targets = set()
        while len(selected_targets) < m:
            chosen = random.choices(nodes, weights=probabilities, k=1)[0]
            selected_targets.add(chosen)
            
        # اتصال یال‌ها به گره جدید
        for target in selected_targets:
            G.add_edge(new_node, target)
            
    return G

# --- تنظیمات و اجرای مدل دست‌ساز ---
N = 5000  # Number of nodes / تعداد گره‌ها
m = 3     # Edges per new node / یال‌های هر گره جدید

print("Building network from scratch / در حال ساخت شبکه از صفر...")
G_custom = custom_barabasi_albert(N=N, m=m)

# استخراج درجات و آماره‌ها
degrees = [d for n, d in G_custom.degree()]
avg_degree = sum(degrees) / N
print(f"Total Nodes (تعداد کل گره‌ها): {G_custom.number_of_nodes()}")
print(f"Total Edges (تعداد کل یال‌ها): {G_custom.number_of_edges()}")
print(f"Average Degree <k> (میانگین درجه): {avg_degree:.2f}")

# محاسبه توزیع درجه P(k)
degree_counts = Counter(degrees)
k_values = np.array(list(degree_counts.keys()), dtype=float)
pk_values = np.array([count / N for count in degree_counts.values()], dtype=float)

# برازش خطی در مقیاس دو-لوگاریتمی
mask = (k_values >= m) & (pk_values > 0)
log_k = np.log10(k_values[mask])
log_pk = np.log10(pk_values[mask])

slope, intercept = np.polyfit(log_k, log_pk, 1)
gamma_calc = -slope

print(f"Theoretical Gamma (گامای تئوری باراباشی): 3.00")
print(f"Calculated Gamma (گامای محاسبه‌شده از کد دست‌ساز): {gamma_calc:.2f}")

# رسم نمودار نهایی
plt.figure(figsize=(8, 5))

# نقاط داده شبیه‌سازی دست‌ساز
plt.scatter(k_values, pk_values, color="darkorange", alpha=0.7, edgecolors="none",
            label="Custom Simulation Data")

# خط برازش قانون توانی
k_fit = np.linspace(k_values[mask].min(), k_values[mask].max(), 100)
pk_fit = 10**(slope * np.log10(k_fit) + intercept)
plt.plot(k_fit, pk_fit, color="navy", linewidth=2, 
         label=rf"Fit Line: $\gamma \approx {gamma_calc:.2f}$")

# تنظیمات محور و برچسب‌ها
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Degree (k) [درجه]")
plt.ylabel("P(k) [فراوانی نسبی]")
plt.title("Custom Barabasi-Albert Distribution & Power-Law Fit\n" + "توزیع درجه شبکه دست‌ساز و برازش خط گاما")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.show()