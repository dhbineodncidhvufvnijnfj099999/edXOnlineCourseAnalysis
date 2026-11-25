-- =============================================================
-- 阶段 6：Power BI 用的汇总表

-- 作用：把 5 个维度的聚合结果一次性算好存表，Power BI 直接读，秒出图
-- =============================================================

USE edx_analysis;

-- 先清旧表（如果之前跑过）
DROP TABLE IF EXISTS edx_pbi_summary;

-- 建表：用 CREATE TABLE ... AS SELECT 一步到位，字段类型自动推断
CREATE TABLE edx_pbi_summary AS

-- --------------------------
-- 维度 1：整体漏斗（1 行）
-- --------------------------
SELECT
    '整体漏斗'                                           AS dimension,
    '注册'                                               AS category,
    COUNT(DISTINCT userid_DI)                            AS registered,
    COUNT(DISTINCT CASE WHEN viewed = 1  THEN userid_DI END) AS viewed,
    COUNT(DISTINCT CASE WHEN explored = 1 THEN userid_DI END) AS explored,
    COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END) AS certified,
    ROUND(
        COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END)
        / NULLIF(COUNT(DISTINCT userid_DI), 0)   -- NULLIF 避免除零
        * 100, 2
    ) AS completion_rate
FROM edx_student_course

UNION ALL

-- --------------------------
-- 维度 2：按课程（16 行）
-- --------------------------
SELECT
    '按课程'                                             AS dimension,
    course_id                                            AS category,
    COUNT(DISTINCT userid_DI)                            AS registered,
    COUNT(DISTINCT CASE WHEN viewed = 1  THEN userid_DI END) AS viewed,
    COUNT(DISTINCT CASE WHEN explored = 1 THEN userid_DI END) AS explored,
    COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END) AS certified,
    ROUND(
        COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END)
        / NULLIF(COUNT(DISTINCT userid_DI), 0)
        * 100, 2
    ) AS completion_rate
FROM edx_student_course
GROUP BY course_id

UNION ALL

-- --------------------------
-- 维度 3：按国家（~20 行）
-- --------------------------
SELECT
    '按国家'                                             AS dimension,
    COALESCE(final_cc_cname_DI, '(未知)')                AS category,
    COUNT(DISTINCT userid_DI)                            AS registered,
    COUNT(DISTINCT CASE WHEN viewed = 1  THEN userid_DI END) AS viewed,
    COUNT(DISTINCT CASE WHEN explored = 1 THEN userid_DI END) AS explored,
    COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END) AS certified,
    ROUND(
        COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END)
        / NULLIF(COUNT(DISTINCT userid_DI), 0)
        * 100, 2
    ) AS completion_rate
FROM edx_student_course
GROUP BY final_cc_cname_DI

UNION ALL

-- --------------------------
-- 维度 4：按教育水平（6 行）
-- --------------------------
SELECT
    '按教育水平'                                         AS dimension,
    COALESCE(LoE_DI, '(未知)')                           AS category,
    COUNT(DISTINCT userid_DI)                            AS registered,
    COUNT(DISTINCT CASE WHEN viewed = 1  THEN userid_DI END) AS viewed,
    COUNT(DISTINCT CASE WHEN explored = 1 THEN userid_DI END) AS explored,
    COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END) AS certified,
    ROUND(
        COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END)
        / NULLIF(COUNT(DISTINCT userid_DI), 0)
        * 100, 2
    ) AS completion_rate
FROM edx_student_course
GROUP BY LoE_DI

UNION ALL

-- --------------------------
-- 维度 5：按性别（3 行）
-- --------------------------
SELECT
    '按性别'                                             AS dimension,
    COALESCE(gender, '(未知)')                           AS category,
    COUNT(DISTINCT userid_DI)                            AS registered,
    COUNT(DISTINCT CASE WHEN viewed = 1  THEN userid_DI END) AS viewed,
    COUNT(DISTINCT CASE WHEN explored = 1 THEN userid_DI END) AS explored,
    COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END) AS certified,
    ROUND(
        COUNT(DISTINCT CASE WHEN certified = 1 THEN userid_DI END)
        / NULLIF(COUNT(DISTINCT userid_DI), 0)
        * 100, 2
    ) AS completion_rate
FROM edx_student_course
GROUP BY gender;

-- =============================================================
-- 验证：跑这 3 句，确认结果和阶段 3-4 一致
-- =============================================================
-- 1. 看汇总表总行数（应该是 45-55 行之间）
SELECT COUNT(*) AS total_rows FROM edx_pbi_summary;

-- 2. 看整体漏斗行（应该和 02_funnel.sql 一致）
SELECT * FROM edx_pbi_summary WHERE dimension = '整体漏斗';

-- 3. 看按课程行数（应该是 16 行，之前阶段4验证过）
SELECT COUNT(*) AS course_rows FROM edx_pbi_summary WHERE dimension = '按课程';

-- 4. 看CS50x（应该完课率最低，之前阶段4验证过是 0.76%）
SELECT category, registered, certified, completion_rate
FROM edx_pbi_summary
WHERE dimension = '按课程' AND category LIKE '%CS50x%';
