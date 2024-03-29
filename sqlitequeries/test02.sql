/* For a 12 hour time period, 
 For each hour, get the average of the concentration */
SELECT
    /*dateTime,
     datetime(dateTime, 'unixepoch', 'localtime') as DT,*/
    count(pm2_5) as countConcentration,
    min(dateTime),
    max(dateTime),
    IFNULL(avg(pm2_5), 0) as avgConcentration
FROM archive
WHERE dateTime >= (unixepoch() / 3600) * 3600 - 39600 + 300
    /* 300 is the archive interval */
    AND dateTime < (unixepoch() / 3600) * 3600 + 3600
GROUP BY (dateTime - 300) / 3600
    /* need to subtract the archive interval to get the correct begin and end range */
    /*HAVING avgConcentration IS NOT NULL*/
ORDER BY dateTime DESC