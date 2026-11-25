-- ===================03_category.sql==========================
-- 目的：按3个维度拆分漏斗，找差异
use edx_analysis;
-- 维度1：按课程ID对比
/*
 group by course_id:按课程分组，每一门课程单独算（注册人数，拿证人数，结业率）用来对比不同课程得转换好坏
 一门课程单独算一套指标，课程之间互相比较。
 case
    when 条件1 then 满足条件1返回的值
    when 条件2 then 满足条件2返回的值
    else 都不满足返回的值
 end
 */
select
    course_id,
    #在这一门课里，有多少个不同的用户报名注册。
    count(distinct userid_DI) as registered,
    count(distinct case when certified=1 then userid_DI end) as certified,
    round(count(distinct case when certified=1 then userid_DI end)
              / count(distinct userid_DI) * 100,2) as completion_rate_pct
from
    edx_student_course
group by course_id
order by completion_rate_pct desc;

-- 维度2：按学生所在国家对比
select
    final_cc_cname_DI as country,
    count(distinct userid_DI) as registered,
    count(distinct case when certified =1 then userid_DI end) as certified,
    round(count(distinct case when certified =1 then userid_DI end) /
          count(distinct userid_DI) * 100,2) as completion_rate_pct
from
    edx_student_course
where
    final_cc_cname_DI is not null
group by
    final_cc_cname_DI
order by
    completion_rate_pct desc;

-- 维度3：按教育水平对比
select
    LoE_DI as education_level,
    count(distinct userid_DI) as registered,
    count(distinct case when certified=1 then userid_DI end) as certified,
    round(count(distinct case when certified=1 then userid_DI end) /
         count(distinct userid_DI) * 100,2 ) as completion_rate_pct
from
    edx_student_course
where
    LoE_DI is not null
group by
    LoE_DI
order by
    completion_rate_pct desc;



