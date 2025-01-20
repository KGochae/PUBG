-- Chapter. SafetyZone table by matchid 
# 배틀그라운드에는 시간에 따라 점점 줄어드는 SafetyZone이라는 장치가 있으며, SafetyZone 안에 들어가야 생존할 수 있는 배틀로얄FPS 게임입니다. 
# 이는 랜덤으로 위치가 정해지기 때문에, 플레이어의 운을 측정할 수 있는 대표적인 지표이죠.
# 즉, 해당 플에이어가 페이즈별로 SafetyZone이 정해지기 전에 이미 들어가 있는 경우라면, 운이 좋다고 판단할 수 있습니다.

-- SafetyZone의 게임 규칙은 다음과 같습니다.  
# 랜덤으로 SafetyZone이 정해집니다.
# 맵에 따라 첫 SafetyZone이 정해지는 시간이 다릅니다. 
# 페이즈별로 줄어드는 SafetyZone의 크기는 고정되어있습니다.

# 아래의 tbl 은 matchId, map, 페이즈 별로 SafetyZone 영역을 정의한 테이블입니다. 
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

# 맵의 규칙에 따라 , 첫 SafetyZone 시작 시간을 지정해줍니다.
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
