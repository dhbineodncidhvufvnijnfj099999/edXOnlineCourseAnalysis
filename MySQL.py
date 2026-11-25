# 把edx_courses.csv导入MySQL（自动跳过index列，布尔字段兼容多种写法转 1/0）
import os
import pandas as pd
from sqlalchemy import create_engine, text
#用绝对路径定位文件：避免“文件找不到”
"""
__file__:当前这个.py文件自身的路径
os.path.abspath():把它转换为绝对路径
os.path.dirname():去掉文件名，得到所在文件夹，即项目根目录
os.path.join(,,,):拼接路径，自动使用当前系统的分隔符
"""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'edx_courses.csv')

# =============读数据===================
"""
on_bad_lines ='skip':当某行的字段个数与表头不一致（例如多一个逗号时）直接丢弃改行，不报错。
这样处理的好处是脚本不会中断，代价是会静默丢失数据。
.tolist():把它转成普通的python列表。
"""
df = pd.read_csv(CSV_PATH, on_bad_lines='skip')
print(f'读取{len(df)}行')
print(f'实际列名：{df.columns.tolist()}')

# ==================删掉没用的index列==================
if 'index' in df.columns:
    df = df.drop(columns=['index'])

# ============3.布尔字段 --》1/0==========
bool_candidates = ['registered', 'viewed', 'explored', 'certified', 'incomplete_flag']
#列表推导式：遍历候选清单，只保留在CSV中真实存在的列，这样即使源文件少了某些列，脚本也不会崩
bool_cols = [c for c in bool_candidates if c in df.columns]

# 兼容 'True'/'true'/'TRUE'/'1'/1/1.0/'yes' 等各种写法
#一个字典，作用是“查找表”，左边是源文件可能出现的写法，后边是MYSQL里能存的整数。
#把数据源里面各种五花八门表示“是/否”的文字，统一翻译成数据库好存的1/0。
BOOL_MAP = {
    'true': 1, 'false': 0,
    '1': 1,    '0': 0,
    '1.0': 1,  '0.0': 0,
    'yes': 1,  'no': 0,
    't': 1,    'f': 0,
}

for col in bool_cols:
    # 去空格 + 转小写，先看看原始值长什么样
    raw = df[col].astype(str).str.strip().str.lower()
    print(f'  [{col}] 原始值：{raw.value_counts().head(5).to_dict()}')
    """
    .map(BOOL_MAP):逐个值去字典里查，查到就换成1/0，查不到（不在字典里）就变成NaN
    .fillna(0):把查不到的NaN全填成0
    .astype(int):转成整数，因为MySQL那边是tinyint，存文本‘true’会报错
    """
    df[col] = raw.map(BOOL_MAP).fillna(0).astype(int)

    print(f'  [{col}] 转换后：{df[col].value_counts().head(3).to_dict()}')

# ============3.5 数值列清洗（空格 → NaN → NULL）==========
num_cols = ['YoB', 'grade', 'nevents', 'ndays_act', 'nplay_video', 'nchapters', 'nforum_posts']
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# ============3.6 日期列清洗==========
for col in ['start_time_DI', 'last_event_DI']:
    if col in df.columns:
        #errors='coerce':转不了的值就变成NaN，而不是报错
        df[col] = pd.to_datetime(df[col], errors='coerce')

# ================4.连接mysql====================
#mysql+pymysql:告诉sqlalchemy使用MySQL的pymysql驱动（pip install pymysql)
engine = create_engine(
    'mysql+pymysql://root:root@localhost:3306/edx_analysis?charset=utf8mb4'
)

# ===== 5. 先清空表，再导入 =====
#with：语句--上下文管理器，负责自动关闭或提交
with engine.connect() as conn:
    conn.execute(text('TRUNCATE TABLE edx_student_course'))
    conn.commit()

df.to_sql('edx_student_course', engine, if_exists='append', index=False, chunksize=10000)
print(f'导入成功！共{len(df)}行')

# ===== 6. 导入后自动校验（省得你再去 DataGrip 查）=====
with engine.connect() as conn:
    row = conn.execute(text(
        'SELECT COUNT(*) AS total, SUM(registered) AS reg, SUM(viewed) AS vie, '
        'SUM(explored) AS exp, SUM(certified) AS cer FROM edx_student_course'
    )).fetchone()
    print(f'✅ 数据库校验：总行数={row[0]}, registered={row[1]}, viewed={row[2]}, explored={row[3]}, certified={row[4]}')