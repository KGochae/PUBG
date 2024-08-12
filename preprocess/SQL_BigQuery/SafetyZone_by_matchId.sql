--Chapter. SafetyZone table by matchid 

WITH tbl as (
              SELECT matchId
                  , MapName
                  , LAG(MIN(_D),1) OVER (PARTITION BY matchId ORDER BY gameState_safetyZoneRadius DESC) AS LAG_D
                  , gameState_safetyZonePosition_x as safetyZone_x
                  , gameState_safetyZonePosition_y as safetyZone_y
                  , gameState_safetyZoneRadius as safetyZone_radius
                  , COUNT(gameState_safetyZoneRadius) as count
                  , ROW_NUMBER() OVER (PARTITION BY matchId ORDER BY matchId ASC) - 1 as phase
              FROM PUBG.bluezone
              WHERE _T ='LogGameStatePeriodic'
              GROUP BY matchId,MapName,gameState_safetyZonePosition_x,gameState_safetyZonePosition_y,gameState_safetyZoneRadius
              HAVING count > 1
            )

SELECT matchId
  , MapName
  , CASE WHEN MapName = 'Savage_Main' and phase = 1 THEN datetime_add(LAG_D, interval 90 second)
      WHEN MapName != 'Savage_Main' and phase = 1 THEN datetime_add(LAG_D, interval 120 second) ELSE LAG_D END AS _D
  , safetyZone_x
  , safetyZone_y
  , safetyZone_radius
  , phase
FROM tbl
WHERE phase > 0