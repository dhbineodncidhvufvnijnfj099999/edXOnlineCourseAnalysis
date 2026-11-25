-- =================05_course_score.sql=========================
/*
 找到高完课率得课程特征，帮运营总结"为什么这门课大家愿意上到最后"
 目的：完课学生的成绩分布 + 找出完课率top10的课程
*/
use edx_analysis;
-- 1.完课学生的成绩分布
# 统计已经拿到证书（certified=1），成绩不为空的这批学生，算出他们的成绩分布：最小值，p25四分位数，中位数苏，。。。
# 拿证学生的成绩整体水平，成绩是集中还是分散，做成绩分布分析。
# 判断课程难度合不合适，是不是大部分通关学生集中在中等分数，有没有大量擦线拿证的人。
WITH ranked AS (
    SELECT
        grade,
        ROW_NUMBER() OVER (ORDER BY grade) AS rn,     -- 每条成绩排个名次（1,2,3...）
        COUNT(*) OVER () AS total   -- 总共有多少条成绩
    FROM edx_student_course
    WHERE certified = 1 AND grade IS NOT NULL
)
select
    round(min(grade),2) as min_grade,
    round(max(case when rn =floor(total * 0.25) then grade end),2) as p25_grade,
    round(max(case when rn=floor(total * 0.5) then grade end),2) as p50_grade,
    round(max(case when rn=floor(total * 0.75) then grade end),2) as p75_grade,
    round(max(grade),2) as max_grade,
    round(avg(grade),2) as avg_grade,
    max(total) as certified_students
from
    ranked;

-- 完课率TOP10课程
/*
 按课程分组，统计每门课的注册人数，拿证人数，拿证率，拿证学生平均分；只保留注册》=500人的课程
 按拿证率从高到低排序，取出前10门
 */
select
    course_id,
    count(distinct userid_DI) as registered_users,
    count(distinct case when certified=1 then userid_DI end) as certified_users,
    round(count(distinct case when certified=1 then userid_DI end)/
          count(distinct userid_DI) * 100,2) as certified_rate_pct,
    round(avg(case when certified=1 then grade end),2) as certified_avg_grade
from
    edx_student_course
group by
    course_id
having
    registered_users >=500  #样本太小的课程完课率没有意义，过滤掉
order by
    certified_rate_pct desc
limit 10;

-- 完课率bottom10课程（对比：什么样的课留不住人）
select
    course_id,
    count(distinct userid_DI) as registered_users,
    count(distinct case when certified=1 then userid_DI end) as certified_users,
    round(count(distinct case when certified=1 then userid_DI end)/
          count(distinct userid_DI) * 100,2) as certified_rate_pct
from
    edx_student_course
group by
    course_id
having
    registered_users >= 500
order by
    certified_rate_pct asc
limit 10;
