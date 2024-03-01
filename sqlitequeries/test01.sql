SELECT dateTime,
    datetime(dateTime, 'unixepoch', 'localtime') as DT,
    pm2_5
FROM archive
WHERE pm2_5 IS NOT NULL
ORDER BY dateTime DESC
LIMIT 288;
