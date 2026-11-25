-- =================04_retention.sql===============
/*
 目的：用窗口函数算“每个学生的课程学习序列”
 用来给学生报多门课，按照注册时间先后排序编号，给每个人自己的行为，按时间先后，打序号。
 */
use edx_analysis;
-- 1.给每个学生的课程注册按时间排序（用窗口函数 row_number)
select
    userid_DI,course_id,start_time_DI,certified,
    #给每个学生的课程注册按注册时间编号（1=第一门，2=第二门。。）
    row_number() over (partition by userid_DI order by start_time_DI) as course_sequence
from
    edx_student_course
where
    start_time_DI is not null
order by
    userid_DI,start_time_DI;
/*
 看：报一门课的学生，多少人拿证；报2门课的学生，多少人拿证。验证：报课越多的学生，是不是更容易至少拿到1个证书。
 1.先按学生汇总：每个学生，一共报了几门，拿证几门（cte）用CTE公共表达式，可以把常用的数据封装成新表，方便操作。
 2.在按{报课数量}分组：统计报N门课的这批学生，有多少人至少拿过一个证书。
 */
-- 2.核心分析：学了N门课的学生，完课率是多少？
with student_course_count as (
    select
        userid_DI,
        count(*) as total_courses,#这个学生一共注册了几门课
        sum(certified=1) as total_certified #这个学生一共完课几门
    from
        edx_student_course
    group by
        userid_DI
)
#按报了n门课学生分组，在报n门课的这群学生里面，百分之多少的人成功拿到至少1个证书
/*
 业务解读：如果报一门课的学生拿证率低，报3门，4门课的拿证率明显更高
 说明：愿意持续报多门课的用户，学习粘性更强，更容易拿证书。
 */
select
    total_courses,
    count(*) as student_count,
    round(sum(total_certified>0) / count(*) * 100,2) as has_any_cert_pct
from
    student_course_count
group by
    total_courses
order by
    total_courses;

