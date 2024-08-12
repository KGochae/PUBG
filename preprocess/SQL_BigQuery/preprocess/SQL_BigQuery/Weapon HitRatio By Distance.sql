-- TODAY QUERY. 난사하는 상황에서의 Shot Ratio by Weapon, Distance
-- 난사의 기준? 5초단위로 남겨지는 데이터에서 10발이상 사용한 경우 "난사"라는 자체가 AR,SMG 같은 돌격소총에게 유의미한 지표이므로 SR 같은 장거리 총의 경우 한계가있다.
-- 데이터가 남겨지는 규칙: 유저가 hit 했을 경우에만 Distance가 남는다. 
-- shot을 했지만 적을 맞추지 못한경우 정확히 누굴 향해 공격했는지 알 수 없고 Distance가 남지 않음 
-- 그러므로 5초단위로 SHOT, HIT 테이블을 따로 만들고, 적을 맞추지 못했지만 5초 안에 적에게 피해를 입혔다면 같은 적을 공격했다고 판단


-- WeaponID 통일 
with dmglog as(
              SELECT *
              , CASE
                      WHEN weapon_itemId = 'Item_Weapon_M16A4_C' THEN 'WeapM16A4_C'
                      WHEN weapon_itemId = 'Item_Weapon_HK416_C' THEN 'WeapHK416_C'
                      WHEN weapon_itemId = 'Item_Weapon_AK47_C' THEN 'WeapAK47_C'
                      WHEN weapon_itemId = 'Item_Weapon_SCAR-L_C' THEN 'WeapSCAR-L_C'
                      WHEN weapon_itemId = 'Item_Weapon_G36C_C' THEN 'WeapG36C_C'
                      WHEN weapon_itemId = 'Item_Weapon_BerylM762_C' THEN 'WeapBerylM762_C'
                      WHEN weapon_itemId = 'Item_Weapon_QBZ95_C' THEN 'WeapQBZ95_C'
                      WHEN weapon_itemId = 'Item_Weapon_Mk47Mutant_C' THEN 'WeapMk47Mutant_C'
                      WHEN weapon_itemId = 'Item_Weapon_AUG_C' THEN 'WeapAUG_C'
                      WHEN weapon_itemId = 'Item_Weapon_Groza_C' THEN 'WeapGroza_C'
                      WHEN weapon_itemId = 'Item_Weapon_ACE32_C' THEN 'WeapACE32_C'
                      WHEN weapon_itemId = 'Item_Weapon_FAMASG2_C' THEN 'WeapFamasG2_C'
                      WHEN weapon_itemId = 'Item_Weapon_K2_C' THEN 'WeapK2_C'
                      WHEN weapon_itemId = 'Item_Weapon_Mini14_C' THEN 'WeapMini14_C'
                      WHEN weapon_itemId = 'Item_Weapon_SKS_C' THEN 'WeapSKS_C'
                      WHEN weapon_itemId = 'Item_Weapon_Mk14_C' THEN 'WeapMk14_C'
                      WHEN weapon_itemId = 'Item_Weapon_Mk12_C' THEN 'WeapMk12_C'
                      WHEN weapon_itemId = 'Item_Weapon_SLR_C' THEN 'WeapSLR_C'
                      WHEN weapon_itemId = 'Item_Weapon_QBU88_C' THEN 'WeapQBU88_C'
                      WHEN weapon_itemId = 'Item_Weapon_VSS_C' THEN 'WeapVSS_C'
                      WHEN weapon_itemId = 'Item_Weapon_Dragunov_C' THEN 'WeapDragunov_C'
                      WHEN weapon_itemId = 'Item_Weapon_FNFal_C' THEN 'WeapFNFal_C'
                      WHEN weapon_itemId = 'Item_Weapon_UZI_C' THEN 'WeapUZI_C'
                      WHEN weapon_itemId = 'Item_Weapon_Vector_C' THEN 'WeapVector_C'
                      WHEN weapon_itemId = 'Item_Weapon_UMP_C' THEN 'WeapUMP_C'
                      WHEN weapon_itemId = 'Item_Weapon_TommyGun_C' THEN 'WeapTommyGun_C'
                      WHEN weapon_itemId = 'Item_Weapon_Thompson_C' THEN 'WeapThompson_C'
                      WHEN weapon_itemId = 'Item_Weapon_Thompson_Old_C' THEN 'WeapThompson_old_C'
                      WHEN weapon_itemId = 'Item_Weapon_PP19Bizon_C' THEN 'WeapPP19Bizon_C'
                      WHEN weapon_itemId = 'Item_Weapon_MP5K_C' THEN 'WeapMP5K_C'
                      WHEN weapon_itemId = 'Item_Weapon_P90_C' THEN 'WeapP90_C'
                      WHEN weapon_itemId = 'Item_Weapon_JS9_C' THEN 'WeapJS9_C'
                      WHEN weapon_itemId = 'Item_Weapon_BizonPP19_C' THEN 'WeapBizonPP19_C'
                      WHEN weapon_itemId = 'Item_Weapon_vz61Skorpion_C' THEN 'Weapvz61Skorpion_C'
                      WHEN weapon_itemId = 'Item_Weapon_S686_C' THEN 'WeapS686_C'
                      WHEN weapon_itemId = 'Item_Weapon_S1897_C' THEN 'WeapS1897_C'
                      WHEN weapon_itemId = 'Item_Weapon_S12K_C' THEN 'WeapS12K_C'
                      WHEN weapon_itemId = 'Item_Weapon_DP12_C' THEN 'WeapDP12_C'
                      WHEN weapon_itemId = 'Item_Weapon_SawedOff_C' THEN 'WeapSawnoff_C'
                      WHEN weapon_itemId = 'Item_Weapon_Saiga12_C' THEN 'WeapSaiga12_C'
                      WHEN weapon_itemId = 'Item_Weapon_Berreta686_C' THEN 'WeapBerreta686_C'
                      WHEN weapon_itemId = 'Item_Weapon_AWM_C' THEN 'WeapAWM_C'
                      WHEN weapon_itemId = 'Item_Weapon_M24_C' THEN 'WeapM24_C'
                      WHEN weapon_itemId = 'Item_Weapon_Kar98k_C' THEN 'WeapKar98k_C'
                      WHEN weapon_itemId = 'Item_Weapon_Win94_C' THEN 'WeapWinchester_C'
                      WHEN weapon_itemId = 'Item_Weapon_MosinNagant_C' THEN 'WeapMosinNagant_C'
                      WHEN weapon_itemId = 'Item_Weapon_LynxAMR_C' THEN 'WeapLynxAMR_C'
                      WHEN weapon_itemId = 'Item_Weapon_Winchester_C' THEN 'WeapWinchester_C'
                      WHEN weapon_itemId = 'Item_Weapon_Mosin_C' THEN 'WeapMosin_C'
                      WHEN weapon_itemId = 'Item_Weapon_Mortar_C' THEN 'WeapMortar_C'
                      WHEN weapon_itemId = 'Item_Weapon_PanzerFaust100M_C' THEN 'WeapPanzerFaust100M_C'
                      WHEN weapon_itemId = 'Item_Weapon_Crossbow_C' THEN 'WeapCrossbow_1_C'
                      WHEN weapon_itemId = 'Item_Weapon_M249_C' THEN 'WeapM249_C'
                      WHEN weapon_itemId = 'Item_Weapon_DP28_C' THEN 'WeapDP28_C'
                      WHEN weapon_itemId = 'Item_Weapon_MG3_C' THEN 'WeapMG3_C'
                      WHEN weapon_itemId = 'Item_Weapon_G18_C' THEN 'WeapG18_C'
                      WHEN weapon_itemId = 'Item_Weapon_M1911_C' THEN 'WeapM1911_C'
                      WHEN weapon_itemId = 'Item_Weapon_M9_C' THEN 'WeapM9_C'
                      WHEN weapon_itemId = 'Item_Weapon_Rhino_C' THEN 'WeapRhino_C'
                      WHEN weapon_itemId = 'Item_Weapon_NagantM1895_C' THEN 'WeapNagantM1895_C'
                      WHEN weapon_itemId = 'Item_Weapon_Deagle_C' THEN 'WeapDeagle_C'
                      WHEN weapon_itemId = 'Item_Weapon_Pan_C' THEN 'WeapPan_C'
                      WHEN weapon_itemId = 'Item_Weapon_Sickle_C' THEN 'WeapSickle_C'
                      WHEN weapon_itemId = 'Item_Weapon_Machete_C' THEN 'WeapMachete_C'
                      WHEN weapon_itemId = 'Item_Weapon_Crowbar_C' THEN 'WeapCrowbar_C'
                      WHEN weapon_itemId = 'Item_Weapon_Grenade_C' THEN 'WeapGrenade_C'
                      WHEN weapon_itemId = 'Item_Weapon_Molotov_Cocktail_C' THEN 'WeapMolotov_Cocktail_C'
                      WHEN weapon_itemId = 'Item_Weapon_SmokeBomb_C' THEN 'WeapSmokeBomb_C'
                      WHEN weapon_itemId = 'Item_Weapon_StickyGrenade_C' THEN 'WeapStickyGrenade_C'
                      WHEN weapon_itemId = 'Item_Weapon_StunGrenade_C' THEN 'WeapStunGrenade_C'
                      ELSE weapon_itemId
                  END AS itemId
              FROM PUBG.dmglog
),


-- 5초 단위의 HIT TABLE
HIT as(
SELECT group_5_sec
      , attacker_name
      , damageCauserName AS itemId
      , victim_name
      , COUNT(*) AS hit
      , SUM(HeadShot) HeadShot, SUM(ArmShot) ArmShot, SUM(TorsoShot) TorsoShot, SUM(LegShot) LegShot, SUM(PelvisShot) PelvisShot
      , SUM(damage) as damage
      , AVG(distance) as distance
FROM (SELECT  matchId
    , TIMESTAMP_SECONDS(DIV(UNIX_SECONDS(_D), 5) * 5) AS group_5_sec
    , _T
    , attacker_name
    , damageTypeCategory, damage
    , damageCauserName
    , victim_name
    , distance
    # Damage 부위 dummy
    , if(damageReason = 'HeadShot',1,0) as HeadShot 
    , if(damageReason = 'ArmShot',1,0) as ArmShot
    , if(damageReason = 'TorsoShot',1,0) as TorsoShot
    , if(damageReason = 'LegShot',1,0) as LegShot
    , if(damageReason = 'PelvisShot',1,0) as PelvisShot
FROM dmglog
WHERE _T = 'LogPlayerTakeDamage' AND damageTypeCategory = 'Damage_Gun' ) A
GROUP BY group_5_sec, attacker_name, damageCauserName, victim_name ),


-- 5초단위의 SHOT Table
SHOT AS(
        SELECT attacker_name
            , group_5_sec
            , itemId
            , count(*) as shot
        FROM (SELECT  matchId
            , _D
            , TIMESTAMP_SECONDS(DIV(UNIX_SECONDS(_D), 5) * 5) AS group_5_sec
            , _T
            , attacker_name
            , damage
            , itemId
        FROM dmglog
        WHERE _T = 'LogPlayerAttack' ) A
        GROUP BY attacker_name, group_5_sec, itemId
)

# 필요시 부위별 ratio 추가
SELECT itemId 
    , distance_category
    , AVG(ratio) * 100 as avg_ratio
FROM (SELECT S.*
    , H.victim_name, H.hit, H.headShot, H.ArmShot, H.TorsoShot, H.LegShot, H.PelvisShot, H.damage, H.distance
    , CASE
        WHEN distance >= 0 AND distance < 10 THEN '0-10m'
        WHEN distance >= 10 AND distance < 20 THEN '10-20m'
        WHEN distance >= 20 AND distance < 30 THEN '20-30m'
        WHEN distance >= 30 AND distance < 40 THEN '30-40m'
        WHEN distance >= 40 THEN '40m+'
        ELSE 'Unknown' END AS distance_category
    , H.hit / S.shot as ratio
FROM SHOT S
  LEFT JOIN HIT H ON S.group_5_sec = H.group_5_sec 
                  AND S.attacker_name = H.attacker_name
                  AND S.itemId = H.itemId
WHERE SHOT >= 10 AND HIT > 0) A
GROUP BY itemId, distance_category
ORDER BY itemId, distance_category