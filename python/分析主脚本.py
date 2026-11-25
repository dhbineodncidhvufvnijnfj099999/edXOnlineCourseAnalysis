# -*- coding: utf-8 -*-
"""
Coursera/edX 课程完课率分析主脚本
"""
import os
from xml.dom.domreg import registered

import pandas as pd
import numpy as np
# ===== 自动定位项目根目录（避免 'data' 目录找不到的报错）=====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===== 1. 加载主数据 =====
df = pd.read_csv(os.path.join(DATA_DIR, 'edx_courses.csv'), on_bad_lines='skip')

# 把布尔字段统一转成 1/0 整数
# ⚠️ 这份 CSV 里已经是 1/0（int64），不是 'True'/'False' 字符串
bool_candidates = ['registered', 'viewed', 'explored', 'certified', 'incomplete_flag']
bool_cols = [c for c in bool_candidates if c in df.columns]
for col in bool_cols:
    num = pd.to_numeric(df[col], errors='coerce')                                    # 1 / 1.0 / 0
    txt = df[col].astype(str).str.strip().str.lower().map({'true': 1, 'false': 0})    # 'True' / 'False'
    df[col] = num.fillna(txt).fillna(0).astype(int)

# 自检：转换写错会立刻暴露，而不是等除法那里除零报错
print(f'🔍 校验：viewed=1 的行数 {df["viewed"].sum():,}  certified=1 的行数 {df["certified"].sum():,}')
assert df['viewed'].sum() > 0, '布尔转换失败：viewed 全是 0，检查上面的转换代码'

# 日期列转日期
df['start_time_DI'] = pd.to_datetime(df['start_time_DI'], errors='coerce')
df['last_event_DI'] = pd.to_datetime(df['last_event_DI'], errors='coerce')

print(f'📐 数据形状：{df.shape[0]:,} 行 × {df.shape[1]} 列')
print(f'📚 唯一学生：{df.userid_DI.nunique():,}')
print(f'🎓 唯一课程：{df.course_id.nunique():,}')
print()

# 漏斗整体（去重学生）
print('=== 漏斗整体（去重唯一学生）===')
reg = df['userid_DI'].nunique()
vie = df[df['viewed']==1]['userid_DI'].nunique()
exp = df[df['explored']==1]['userid_DI'].nunique()
cer = df[df['certified']==1]['userid_DI'].nunique()

print(f'注册：{reg:,} 人')
print(f'观看：{vie:,} 人 → 转化率 {vie/reg*100:.1f}%')
print(f'探索：{exp:,} 人 → 转化率 {exp/vie*100:.1f}%')
print(f'证书：{cer:,} 人 → 转化率 {cer/exp*100:.1f}%')
print(f'全链路：{cer/reg*100:.1f}%')


#================2.按课程拆分漏斗==========================
print('\n======按完课人数率（全部16门课）=====')
by_course = df.groupby('course_id').agg(
    registered =('userid_DI','nunique'),
    certified =('certified','sum')
).reset_index()
by_course['completion_rate'] = by_course['certified'] / by_course['registered'] *100
by_course=by_course.sort_values('completion_rate',ascending=False)

#过滤小样本：注册人数<500的课程完课率没有统计意义
by_course_filtered = by_course[by_course['registered'] >= 500].copy()
print(by_course_filtered.to_string(index=False))

#============3.统计学：完课学生VS未完课学生的成绩对比=================
print('\n=========完课 vs 未完课 学生的成绩对比==========')
df['grade'] = pd.to_numeric(df['grade'], errors='coerce')
completed_grade = df.loc[df['certified']==1,'grade'].dropna()
not_completed_grade = df.loc[df['certified']==0,'grade'].dropna()
print(f'完课学生 n={len(completed_grade)},均值{completed_grade.mean():.3f},中位数{completed_grade.median():.3f}')
print(f'未完课学生 n={len(not_completed_grade)},均值{not_completed_grade.mean():.3f},中位数{not_completed_grade.median():.3f}')

#=============相关性：学习活跃度 * 完课===================
print('\n====学习活跃度 vs 完课 的相关性====')
#计算两个学习活跃指标（活跃天数、交互次数）和「是否完课拿证」的相关程度，看哪个行为和完课的关系更强。
df_corr = df[['ndays_act','nevents','certified']].dropna()
print(df_corr.corr()['certified'].sort_values(ascending=False))

#==============国家维度========================
#保留中间结果，给后续可视化用
#assign的作用：在不改动原始df的前提下，新增/修改一列，返回新的DataFrame的搭配fillna('未知’）防止groupby的时候NaN被丢掉，统计失真
#df.assign(新列名 = 列的计算逻辑)
by_country = (df.assign(country=df['final_cc_cname_DI'].fillna('未知')).groupby('country').agg(
    registered=('userid_DI','nunique'),
    certified=('certified','sum')).reset_index()
)
by_country['completion_rate'] = by_country['certified'] / by_country['registered']*100
print('\n====国家完课率top10（注册人数》=1000）==========')
print(by_country[by_country['registered']>=500].sort_values('completion_rate',ascending=False).head(10).to_string(index=False))

#==================学历维度=======================
by_edu =(df.assign(edu=df['LoE_DI'].fillna('未知')).groupby('edu').agg(
    registered=('userid_DI', 'nunique'),
    certified =('certified', 'sum')
).reset_index())
by_edu['completion_rate'] = by_edu['certified']/by_edu['registered']*100
print('\n=============学历完课率=====================')
print(by_edu.sort_values('completion_rate',ascending=False).to_string(index=False))

#===========7.保留中间结果（后面可视化要用到）======================
funnel_data = pd.DataFrame({
    'stage':['注册','观看','探索','证书'],
    'users':[reg,vie,exp,cer]
})
funnel_data.to_csv(os.path.join(OUTPUT_DIR,'funnel_data.csv'),index=False,encoding='utf-8-sig')
by_course_filtered.to_csv(os.path.join(OUTPUT_DIR, 'by_course.csv'), index=False, encoding='utf-8-sig')
by_country.to_csv(os.path.join(OUTPUT_DIR, 'by_country.csv'), index=False, encoding='utf-8-sig')
by_edu.to_csv(os.path.join(OUTPUT_DIR, 'by_education.csv'), index=False, encoding='utf-8-sig')
print('\n中间结果已保存到output/文件夹:' 'funnel_data.csv / by_course.csv / by_country.csv / by_education.csv')