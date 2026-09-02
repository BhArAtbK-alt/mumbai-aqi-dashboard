SELECT location_name, COUNT(*) as reading_count 
FROM readings 
GROUP BY location_name 
ORDER BY reading_count DESC;

SELECT location_name, pollutant, value, unit, recorded_at 
FROM readings 
WHERE pollutant = 'pm25' 
ORDER BY value DESC 
LIMIT 5;

SELECT pollutant, ROUND(AVG(value)::numeric, 2) as avg_value, unit 
FROM readings 
GROUP BY pollutant, unit;
