SELECT
    tablespace_name,
    SUM(bytes) / 1024 / 1024 AS total_size_mb
FROM
    dba_data_files
WHERE
    tablespace_name = 'USERS'
GROUP BY
    tablespace_name;

--SELECT table_name, tablespace_name
--FROM user_tables
--WHERE table_name = 'STDA_STATS';