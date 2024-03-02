/* For a 12 hour time period, 
 For each hour, get the average of the concentration */
SELECT
    (unixepoch() /3600 ) * 3600 + 3600 as epoch,
    /*datetime((unixepoch() / 3600) * 3600 + 3600, 'unixepoch', 'localtime') as DTN,*/
    dateTime,
    datetime(dateTime, 'unixepoch', 'localtime') as DT,
    count(pm2_5) as countConcentration,
    /*min(pm2_5) as minConcentration,*/
    /*max(pm2_5) as maxConcentration,*/
    min(dateTime),
    max(dateTime),
    datetime(min(dateTime), 'unixepoch', 'localtime') as minDT,
    datetime(max(dateTime), 'unixepoch', 'localtime') as maxDT,
    avg(pm2_5) as avgConcentration
FROM archive
WHERE dateTime >= (unixepoch() / 3600) * 3600 - 39600
    AND dateTime < (unixepoch() / 3600) * 3600 + 3600
GROUP BY (dateTime - 300) / 3600 /* need to subtract the archive interval to get the correct begin and end range */
HAVING avgConcentration IS NOT NULL
ORDER BY dateTime ASC