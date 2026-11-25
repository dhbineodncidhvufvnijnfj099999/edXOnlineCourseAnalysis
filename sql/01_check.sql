#================01_check.sql================================
#目的：快速诊断数据质量（数据质量检测）
-- 1.每个字段的空值数量
use edx_analysis;
select
    count(*) as total,
    sum(course_id is null) as null_course_id,
    sum(userid_DI is null) as null_userid,
    sum(registered is null) as null_registered,
    sum(viewed is null) as null_viewed,
    sum(explored is null) as null_explored,
    sum(certified is null) as null_certified,
    sum(final_cc_cname_DI is null) as null_country,
    sum(LoE_DI is null) as null_education,
    sum(gender is null) as null_gender,
    sum(grade is null) as null_grade
from
    edx_student_course;