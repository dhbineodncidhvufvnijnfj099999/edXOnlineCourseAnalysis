use edx_analysis;
show tables;
-- 建表 SQL：edx_student_course（HarvardX 学生 × 课程行为表）--comment相当于备注 engine-引擎
CREATE TABLE IF NOT EXISTS edx_student_course (
    course_id          VARCHAR(64)     COMMENT '课程ID，如 HarvardX/CS50x/2012',
    userid_DI          VARCHAR(32)     COMMENT '学生匿名ID',
    registered         TINYINT(1)      COMMENT '是否注册 1=是 0=否',
    viewed             TINYINT(1)      COMMENT '是否观看过视频 1=是 0=否',
    explored           TINYINT(1)      COMMENT '是否探索过课程 1=是 0=否',
    certified          TINYINT(1)      COMMENT '是否拿证书（完课）1=是 0=否',
    final_cc_cname_DI  VARCHAR(64)     COMMENT '学生所在国家',
    LoE_DI             VARCHAR(32)     COMMENT '最高教育水平',
    YoB                INT             COMMENT '出生年份',
    gender             VARCHAR(8)      COMMENT '性别 M/F/unknown',
    grade              DECIMAL(5,4)   COMMENT '最终成绩 0.0-1.0',
    start_time_DI      DATETIME        COMMENT '注册时间',
    last_event_DI      DATETIME        COMMENT '最后一次登录时间',
    nevents            INT             COMMENT '总操作次数',
    ndays_act          INT             COMMENT '活跃天数',
    completed          TINYINT(1)      COMMENT '是否完成所有章节',
    nplay_video        INT             COMMENT '播放视频次数',
    nchapters          INT             COMMENT '浏览章节数',
    nforum_posts       INT             COMMENT '论坛发帖数',
    roles              VARCHAR(32)     COMMENT '学生角色 learner/staff',
    incomplete_flag    TINYINT(1)      COMMENT '未完成标记',
    PRIMARY KEY (userid_DI, course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='HarvardX 学生课程行为表';
ALTER TABLE edx_analysis.edx_student_course DROP COLUMN completed;
SELECT COUNT(*) FROM edx_analysis.edx_student_course;
SELECT SUM(registered), SUM(viewed), SUM(explored), SUM(certified) FROM edx_analysis.edx_student_course;

#事务测试
#--1.先看当前行数
select count(*) from edx_student_course;
#--2.手动开事务，删1条
start transaction;
delete from edx_student_course limit 1;
select count(*) from edx_student_course;
#--3.立刻回滚，数据回来！
rollback;
select count(*) from edx_student_course;