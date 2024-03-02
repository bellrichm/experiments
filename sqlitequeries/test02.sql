/* Need to double check the inclusivity of the timestamps */
SELECT dateTime,
    datetime(dateTime, 'unixepoch', 'localtime') as DT,
    count(pm2_5) as countConcentration,
    /*min(pm2_5) as minConcentration,*/
    /*max(pm2_5) as maxConcentration,*/
    avg(pm2_5) as avgConcentration
FROM archive
WHERE dateTime >= 1709366400
    AND dateTime < 1709409600
GROUP BY dateTime / 3600
HAVING avgConcentration IS NOT NULL
ORDER BY dateTime DESC