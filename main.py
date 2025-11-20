import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# file 'student_lifestyle_dataset.csv' phải nằm cùng thư mục hoặc cung cấp đường dẫn đầy đủ đến file
try:
    df = pd.read_csv('student_lifestyle_dataset.csv')
except FileNotFoundError:
    print("Không tìm thấy file 'student_lifestyle_dataset.csv'. Vui lòng kiểm tra lại đường dẫn.")
    exit()

sns.set_theme(style="whitegrid", palette="viridis")

plt.figure(figsize=(10, 6))
scatter_plot = sns.scatterplot(
    data=df,
    x='Study_Hours_Per_Day',
    y='Grades',
    hue='Stress_Level',
    hue_order=['Low', 'Moderate', 'High'], 
    palette='viridis_r', 
    alpha=0.8,
    s=50 
)

sns.regplot(
    x='Study_Hours_Per_Day',
    y='Grades',
    data=df,
    scatter=False, 
    color='red',
    line_kws={'linestyle':'--'}
)

scatter_plot.set_title('Mối quan hệ giữa Giờ học, Điểm số và Mức độ căng thẳng', fontsize=16, weight='bold')
scatter_plot.set_xlabel('Số giờ học mỗi ngày', fontsize=12)
scatter_plot.set_ylabel('Điểm số', fontsize=12)

plt.legend(title='Mức độ căng thẳng')
plt.tight_layout()
plt.show()
