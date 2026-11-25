"""
FastAPI后端：把edx课程分析结果封装成rest接口
rest：是一套接口设计规范，基于http协议，用get/host等方法操作资源，一般返回json格式
我用fastAPI把edx课程的漏斗，完课率等分析结果，封装成rest接口，前端或者BI公管局通过网络请求，直接拿到分析指标，不用重复运行数据分析脚本。
"""
from fastapi import FastAPI,HTTPException
#跨域中间件
#浏览器有安全限制：前端网页和后端网页接口，如果域名/端口不一样，浏览器会直接拦住前端请求，拿不到数据。
#允许这个前端来调用我的FastAPI接口。
from fastapi.middleware.cors import CORSMiddleware
#定义数据模型，自动校验数据类型，自动生成接口文档，自动转json(少些校验代码，接口文档/docs会自动识别这个模型，展示给调用方看）
from pydantic import BaseModel
import pandas as pd
import os
import sys

app = FastAPI(title = 'edX 课程分析 API',version='1.0')
#============CORS中间件（允许前端跨域调用）===============
"""
origins=来源地址（前端网址）*=通配符，允许任意前端地址来访问这个后端接口
methods=http请求方式：get，post，put，delete 允许所有的请求方式，数据分析接口大多是get查询
headers=请求头（请求附带的额外信息，比如token，允许前端携带任意请求头过来。
==》放开全部限制，允许任何前端网页，任何请求方式，任何请求头，调用我这个FastAPI接口，解决浏览器跨域报错。
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)
#==================加载数据（启动时读一次，不重复访问MySQL）======================
DATA_DIR=os.path.join(os.path.dirname(__file__),'..','output')
df_funnel = pd.read_csv(os.path.join(DATA_DIR,'funnel_data.csv'))
df_course = pd.read_csv(os.path.join(DATA_DIR,'by_course.csv'))
df_country = pd.read_csv(os.path.join(DATA_DIR,'by_country.csv'))

#============接口1：课程TOP10===========================
@app.get('/api/courses')
def get_courses(top_n:int =10):
    """返回完课率 TOP N的课程（默认10）"""
    #top:完课率最高的N门课的小表格（DataFrame）
    top = df_course.sort_values('completion_rate',ascending=False).head(top_n)
    #打包返回给前端
    return {
        'total':len(top),
        'courses':top.to_dict('records') #把表格转成python字典，records是模式：一行=一个字典
    }

#=============接口2：漏斗整体======================
@app.get('/api/funnel')
def get_funnel():
    """返回漏斗 环节的人数和转化率"""
    stages = df_funnel['stage'].tolist()
    users = df_funnel['users'].tolist()

    result = []
    for i, (stage, count) in enumerate(zip(stages, users)):
        prev = users[i - 1] if i > 0 else count
        rate = round(count / prev * 100,
                     2) if prev > 0 else 100
        result.append({
            'stage': stage,
            'users': int(count),
            'conversion_from_prev': rate
        })
        #返回的结果是一个大列表，里面包含四个字典。---》result
    return {'funnel': result}


#============接口3：指定课程详情========================
@app.get('/api/course/{course_id}')
def get_course_detail(course_id:str):
    """返回指定课程的注册人数、完课率、国家分布
    输入课程编号--在课程表里搜搜--找不到就报404--找到了就拿出第一条，返回他的注册人数，证书人数，完课率"""
    #模糊查找，包含这个文字就算找到，不区分大小写，空值直接跳过,去course_id这1列搜索你写的course_id,返回的是一行数据
    match = df_course[df_course['course_id'].str.contains(course_id,case=False,na=False)]
    if match.empty:
        raise HTTPException(status_code=404,detail=f'未找到包含"{course_id}"的课程')
    row = match.iloc[0]
    return {
        'course_id':str(row['course_id']),
        'registered':int(row['registered']),
        'certified': int(row['certified']),
        'completion_rate':round(row['completion_rate'],2)
    }
"""
启动FastAPI的两个方法：
1.在终端terminal输入：uvicorn main:app --reload --port 8000(reload:热更新，你改代码不用重启）
2.方式2如下：
"""
if __name__ == '__main__':
    import uvicorn
    # 把当前文件所在目录加入模块搜索路径，保证 "main:app" 能被找到
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    # reload 模式必须传导入字符串 "模块名:app"，不能传 app 对象
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


