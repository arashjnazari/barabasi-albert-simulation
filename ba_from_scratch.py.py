import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

# 1. Generate Barabasi-Albert Network / ساخت شبکه آماده
N = 5000  # Number of nodes / تعداد گره‌ها
m = 3     # Edges per new node / تعداد یال‌های گره جدید
G = nx.barabasi_albert_graph(n=N, m=m)

# 2. Extract Degrees and Statistics / استخراج درجات و آماره‌ها
degrees = [d for n, d in G.degree()]
avg_degree = sum(degrees) / N
print(f"Total Nodes (تعداد کل گره‌ها): {G.number_of_nodes()}")
print(f"Total Edges (تعداد کل یال‌ها): {G.number_of_edges()}")
print(f"Average Degree <k> (میانگین درجه): {avg_degree:.2f}")

# 3. Calculate Degree Distribution P(k) / محاسبه توزیع درجه
degree_counts = Counter(degrees)
k_values = np.array(list(degree_counts.keys()), dtype=float)
pk_values = np.array([count / N for count in degree_counts.values()], dtype=float)

# 4. Power-law Fitting (Log-Log) / برازش قانون توانی در مقیاس دو-لوگاریتمی
# فیلتر برای حذف نویز گره‌های اولیه و مقادیر صفر
mask = (k_values >= m) & (pk_values > 0)
log_k = np.log10(k_values[mask])
log_pk = np.log10(pk_values[mask])

# محاسبه شیب (منفی گاما)
slope, intercept = np.polyfit(log_k, log_pk, 1)
gamma_calc = -slope

print(f"Theoretical Gamma (گامای تئوری باراباشی): 3.00")
print(f"Calculated Gamma (گامای محاسبه‌شده): {gamma_calc:.2f}")

# 5. Plotting / رسم نمودار
plt.figure(figsize=(8, 5))

# الف) رسم نقاط داده تجربی
plt.scatter(k_values, pk_values, color="royalblue", alpha=0.7, edgecolors="none",
            label="Data (NetworkX)")

# ب) رسم خط برازش منفی گاما (استفاده از r برای جلوگیری از خطای متنی)
k_fit = np.linspace(k_values[mask].min(), k_values[mask].max(), 100)
pk_fit = 10**(slope * np.log10(k_fit) + intercept)
plt.plot(k_fit, pk_fit, color="crimson", linewidth=2, 
         label=rf"Fit Line: $\gamma \approx {gamma_calc:.2f}$")

# تنظیمات مقیاس و برچسب‌های دو زبانه
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Degree (k) [درجه]")
plt.ylabel("P(k) [فراوانی نسبی]")
plt.title("Barabasi-Albert Degree Distribution & Power-Law Fit\n" + "توزیع درجه و برازش خط گاما")
plt.legend()
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.tight_layout()
plt.show()