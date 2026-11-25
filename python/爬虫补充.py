"""#爬虫补充：课程名、所属机构、学习时长、语言
#课程列表：https://api.coursera.org/api/courses.v1
#机构名称：https://api.coursera.org/api/partners.v1
普通网页url：返回html（给人看），API（url）返回json（给程序读）
很多项目的最优路径：优先找开发者文档--如果没有，浏览器抓包找XHR--如果找不到，才解析页面DOM
用API比解析DOM稳定的多，代价是可能拿不到全部字段（比如价格就没了）
os库主要是用来--》操作系统路径、文件、文件夹工具包
os.path（专门处理路径）
os.makedirs(建文件夹）
os.path.join(拼接路径）
os.path.abspath/dirname(拿绝对路径，上一级目录）
DOM：document object model 文档对象模型（浏览器拿到网页html，把一长串文本解析成一颗（节点树）
--》网页渲染出来的结构树，给浏览器展示
API：直接拿原始json数据（给程序读）
"""
from wsgiref import headers

import pandas as pd
import requests
import os
#======自动定位根目录（避免‘data’目录找不到）===================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')  #拼接路径，在项目根目录下面生成data文件
os.makedirs(DATA_DIR, exist_ok=True)

# ===== 请求头（模拟浏览器）=====
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
# ===== 第 1 步：拿课程列表（前 50 门）=====
url = 'https://api.coursera.org/api/courses.v1'
params = {
'start': 0,
    'limit': 50,
    'fields': 'name,slug,workload,primaryLanguages,partnerIds'
}
print('开始爬取coursera课程~')
resp = requests.get(url,headers=headers,params=params,timeout=20)
#校验请求有没有成功，失败就出来提醒，抛出HTTPError
resp.raise_for_status()
data = resp.json()
# ===== 把 JSON 整理成列表 =====
courses = [] #创建一个空列表，准备装一堆字典。往列表里面塞进去一个字典
for c in data['elements']:
    courses.append({
        'course_name':c.get('name',''),  #安全取，如果有name--》返回它的值，如果没有--》返回默认值’‘
        'slug':c.get('slug',''),
        'workload':c.get('workload',''),
        'language':(c.get('primaryLanguages') or [''])[0], #如果能拿到数组，就取数组第一个，拿不到就用['']兜底，在取第一个得到空字符串。
        'partner_id':(c.get('partnerIds') or [''])[0],
    })
df = pd.DataFrame(courses) #转成pandas表格dataframe
print(f'拿到{len(df)}门课程')

# ===== 第 2 步：把 partner_id 换成机构名字 =====
ids = ','.join([x for x in df['partner_id'].unique() if x]) #使用英文逗号，把列表里所有ID拼接成一长串字符串
p_url = 'https://api.coursera.org/api/partners.v1'
p_resp = requests.get(p_url,headers=headers,params={'ids':ids},timeout=20)
partner_map = {p['id']:p['name'] for p in p_resp.json()['elements']}
#根据id查表翻译成机构名字，找不到就填未知，然后删掉原始id列
df['partner_name'] = df['partner_id'].map(partner_map).fillna('未知')
df = df.drop(columns=['partner_id'])

# ===== 第 3 步：保存 =====
save_path = os.path.join(DATA_DIR,'coursera_scraped.csv')
df.to_csv(save_path,index=False,encoding='utf-8-sig')
print(f'文件已保存到{save_path}')
print()
print('前5门课：')
print(df.head())