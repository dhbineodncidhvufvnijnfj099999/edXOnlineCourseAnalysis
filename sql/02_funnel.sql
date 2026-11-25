-- ====================02_funnel.sql=====================
-- 目的：算4环节漏斗整体转化率
-- 用CTE把每一步的人数先算出来 common table expression（公用表达式）
# 用with开头的sql语法，用来定义一张虚拟临时表，只在这一段sql里面生效。
use edx_analysis;
with funnel_counts as(
    select
         #注册（去重，一个学生算一次，一个学生可能报多门课程）
        count(distinct userid_DI) as registered_users,
        #观看的人数(满足观看视频，且不重复的用户一共有多少人--userid_DI）
        count(distinct case when viewed=1 then userid_DI end) as viewed_users,
        #探索的人数
        count(distinct case when explored=1 then userid_DI end) as explored_users,
        #拿证书的人数
        count(distinct case when certified=1 then userid_DI end ) as certified_users
    from
        edx_student_course
)

-- 算转化率
select
    registered_users,
    viewed_users,
    round(viewed_users / registered_users * 100,2) as registered_to_viewed_pct,
    explored_users,
    round(explored_users / viewed_users * 100,2) as viewed_to_explored_pct,
    certified_users,
    round(certified_users / explored_users * 100,2) as explored_to_certified_pct,
    round(certified_users / registered_users * 100,2) as overall_conversion_pct
from
    funnel_counts;


