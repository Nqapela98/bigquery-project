SELECT DATE(timestamp) as date,
    event_type,
    count(*) 
FROM `deft-advice-459518-c8.analytics.events` 
group by 1,2
order by 1,2