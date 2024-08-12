-- Farming Speed table (User Itempickup speed)
# 경기, 유저별로 아이템을 줍는 속도를 계산
# 조건1 각 유저별로 아이템을 첫 파밍하는 순간부터 3분동안
# 조건2 아이템간의 거리가 50cm 미만인 경우에만

# 이전 로그간의 차이를 구하기위해 lag
WITH tbl as(
                SELECT  matchId, character_name, _D, item_itemId, character_location_x, character_location_y, character_location_z
                      , LAG(_D,1) OVER(PARTITION BY matchId,character_name ORDER BY _D) AS LAG_D
                      , LAG(character_location_x,1) OVER(PARTITION BY matchId,character_name ORDER BY _D) AS LAG_X
                      , LAG(character_location_y,1) OVER(PARTITION BY matchId,character_name ORDER BY _D) AS LAG_Y
                      , LAG(character_location_z,1) OVER(PARTITION BY matchId,character_name ORDER BY _D) AS LAG_Z
                      , timestamp_add(MIN(_D) OVER(PARTITION BY matchId,character_name), INTERVAL 180 second) AS LAST_D # 각 유저별 파밍 마지노선 시간
                FROM PUBG.farming
                WHERE _T in('LogItemPickup')
          )

SELECT character_name
    , AVG(speed) as farming_speed
FROM(
      SELECT matchId
            , character_name
            , _D - LAG_D AS speed
      FROM tbl
      WHERE SQRT(POW((LAG_X - character_location_x),2) 
                + POW((LAG_Y - character_location_y),2) 
                + POW((LAG_Z - character_location_z),2)) / 100 < 0.5 
        AND _D < LAST_D
      ) a
GROUP BY character_name

