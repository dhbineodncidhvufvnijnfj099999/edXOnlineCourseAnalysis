# -*- coding: utf-8 -*-
"""
四张可视化图脚本
数据来源：output/ 里的 4 个中间结果 CSV + data/edx_courses.csv
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 显示中文
matplotlib.rcParams['axes.unicode_minus'] = False                          # 显示负号

# ===== 自动定位项目根目录（避免路径报错）=====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== 加载中间结果（从分析主脚本.py 保存的 CSV 来）=====
funnel_data = pd.read_csv(os.path.join(OUTPUT_DIR, 'funnel_data.csv'))
by_course   = pd.read_csv(os.path.join(OUTPUT_DIR, 'by_course.csv'))
by_country  = pd.read_csv(os.path.join(OUTPUT_DIR, 'by_country.csv'))
by_edu      = pd.read_csv(os.path.join(OUTPUT_DIR, 'by_education.csv'))

# ===== 主数据（图 4 箱线图要用 ndays_act / certified =====
df = pd.read_csv(os.path.join(DATA_DIR, 'edx_courses.csv'), on_bad_lines='skip')
df['certified'] = pd.to_numeric(df['certified'], errors='coerce').fillna(0).astype(int)
df['ndays_act'] = pd.to_numeric(df['ndays_act'], errors='coerce')

print('数据加载完成')


#%% 图 1：漏斗图（横向条形）
fig, ax = plt.subplots(figsize=(10, 5))
stages = funnel_data['stage'].tolist()
users  = funnel_data['users'].tolist()
colors = ['#4CAF50', '#FFC107', '#FF9800', '#F44336']
y_pos = range(len(stages))
bars = ax.barh(y_pos, users, color=colors, height=0.5)

ax.set_yticks(y_pos)
ax.set_yticklabels(stages, fontsize=12)
ax.set_xlabel('去重学生数', fontsize=12)
ax.set_title('edX 在线课程完课率漏斗（去重唯一学生）', fontsize=14)

# 每个条上标人数 + 环比转化率
for i, (stage, count) in enumerate(zip(stages, users)):
    if i > 0:
        pct = count / users[i-1] * 100
        ax.text(count + users[0]*0.01, i, f'{count:,}  (环比 {pct:.1f}%)',
                va='center', fontsize=10)
    else:
        ax.text(count + users[0]*0.01, i, f'{count:,}  (100%)',
                va='center', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '图1_漏斗图.png'), dpi=150)
plt.close()
print('✅ 图1 漏斗图 已保存')


#%% 图 2：课程四象限散点图（注册量 × 完课率，气泡=完课人数）
fig, ax = plt.subplots(figsize=(10, 8))
ax.scatter(
    x=by_course['registered'],
    y=by_course['completion_rate'],
    s=by_course['certified'] * 0.5,   # 气泡大小 = 完课人数
    c='steelblue', alpha=0.7
)

# 标明星课程（完课率 TOP5）
for _, row in by_course.nlargest(5, 'completion_rate').iterrows():
    short_name = row['course_id'].split('/')[1] if '/' in str(row['course_id']) else str(row['course_id'])
    ax.annotate(short_name,
                (row['registered'], row['completion_rate']),
                fontsize=8, ha='left', va='bottom')

ax.set_xlabel('注册人数（越多 = 市场越大）', fontsize=12)
ax.set_ylabel('完课率 %（越高 = 体验越好）', fontsize=12)
ax.set_title('课程四象限：大市场 vs 高完课率', fontsize=14)
ax.axvline(by_course['registered'].median(),  color='gray', linestyle='--', label='注册中位数')
ax.axhline(by_course['completion_rate'].median(), color='gray', linestyle='--', label='完课率中位数')
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '图2_课程四象限.png'), dpi=150)
plt.close()
print('✅ 图2 课程四象限 已保存')


#%% 图 3：注册人数 TOP15 国家的完课率对比
top_countries = by_country.sort_values('registered', ascending=False).head(15)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(top_countries['country'], top_countries['completion_rate'], color='teal')
ax.set_xlabel('国家/地区', fontsize=12)
ax.set_ylabel('完课率 %', fontsize=12)
ax.set_title('注册人数 TOP15 国家的完课率对比', fontsize=14)
plt.xticks(rotation=45, ha='right')

for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.2,
            f'{h:.1f}%', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '图3_国家完课率.png'), dpi=150)
plt.close()
print('✅ 图3 国家完课率 已保存')


#%% 图 4：完课 vs 未完课学生的活跃天数箱线图
completed_days     = df.loc[df['certified'] == 1, 'ndays_act'].dropna()
not_completed_days = df.loc[df['certified'] == 0, 'ndays_act'].dropna()

fig, ax = plt.subplots(figsize=(8, 6))
ax.boxplot(
    [not_completed_days.values, completed_days.values],
    patch_artist=True,
    boxprops=dict(facecolor='lightblue'),
    medianprops=dict(color='red', linewidth=2)
)
plt.xticks([1, 2], ['未完课学生', '完课学生'], fontsize=11)
ax.set_ylabel('活跃天数', fontsize=12)
ax.set_title('完课 vs 未完课学生的活跃天数差异', fontsize=14)

# 中位数文字标注
plt.text(2, completed_days.median() + 3,
         f'完课中位数: {completed_days.median():.0f} 天', ha='center', color='red')
plt.text(1, not_completed_days.median() + 3,
         f'未完课中位数: {not_completed_days.median():.0f} 天', ha='center', color='red')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '图4_活跃天数箱线图.png'), dpi=150)
plt.close()
print('✅ 图4 活跃天数箱线图 已保存')

print('\n🎉 四张图全部画完，保存在 output/ 文件夹')
