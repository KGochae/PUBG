# ----- json, dataframe ...etc ------#
import re
import json
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_elements import dashboard
from streamlit_elements import nivo, elements, mui, media
from sklearn.preprocessing import MinMaxScaler

import datetime
import random
import requests
import time
from scipy.stats import gaussian_kde
from scipy.spatial.distance import euclidean


# def prepro
from prepro import dmg_gun_df, dmg_by_distance, item_score, streak_distance_DUO

# ------ image matplotlib ----------- #
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.preprocessing import MinMaxScaler
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from scipy.stats import gaussian_kde

# matplotlib 에러
import matplotlib
matplotlib.use('Agg')  # Use the 'agg' backend


# 일부 css
with open( "main.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
pd.set_option('mode.chained_assignment',  None)


# PUBG API URL 및 API KEY 설정
API_URL = "https://api.pubg.com"
API_KEY = (
    # .stremlit/secrets.toml
    st.secrets["PUBGAPI"]
).get('API_KEY')

# 요청 헤더 설정
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/vnd.api+json"
}

# player id 별 matchid
def get_player_id(player_name):
    endpoint = f"/shards/steam/players?filter[playerNames]={player_name}"
    response = requests.get(API_URL + endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            match_ids = data['data'][0]['relationships']['matches']['data']
            match_ids = [match['id'] for match in match_ids][0]
            return match_ids
        else:
            print("플레이어를 찾을 수 없습니다.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None



# matchid 별 경기
def get_match_details(match_ids):
    all_match_details = []

    for match_id in match_ids:
        url = f'https://api.pubg.com/shards/steam/matches/{match_id}'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            all_match_details.append(response.json())
        else:
            print(f"Error: {response.status_code} for match ID {match_id}")

    return all_match_details
    




# matchid 별 경기
def get_match_detail(match_ids):
    url = 'https://api.pubg.com/shards/steam/matches/{}'
    url = url.format(match_ids)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


# csv 파일 업로드
@st.cache_data
def load_csv_in_chunks(chunk_size=100000):
    chunks = pd.read_csv('damage_log_data_all.csv', chunksize=chunk_size)
    return pd.concat(chunks)




# 데이터 실시간 수집용 사이드바
with st.sidebar:
    with st.form(key ='searchform'):
        player_name = st.text_input("Search User")        

        API_KEY = st.text_input("api_key",
                                type = "password"
                               )
        submit_search = st.form_submit_button(label='Submit')

    with st.form(key='loadcsv'):
        csv_load = st.form_submit_button(label='CSV')


if submit_search :
    match_ids = get_player_id(player_name)
    match_datas = get_match_detail(match_ids)
    st.session_state.match_ids = match_ids
    st.session_state.match_datas = match_datas

if csv_load:
    damage_gun_df = load_csv_in_chunks(chunk_size=100000)
    
    # damage_gun_df = dmg_gun_df(data)        

    # item_score_df = item_score(damage_gun_df)
    merged_df, damage_df = dmg_by_distance(damage_gun_df,s='5s')
    recoil_df = dmg_by_distance(damage_gun_df, s='1s')
    streak_df = streak_distance_DUO(damage_gun_df, damage_df)

    # st.session_state.item_score_df = item_score_df
    st.session_state.merged_df = merged_df
    st.session_state.recoil_df = recoil_df
    st.session_state.streak_df = streak_df
    
if hasattr(st.session_state, 'match_ids'):
    match_ids = st.session_state.match_ids

if hasattr(st.session_state, 'match_datas'):
    match_datas = st.session_state.match_datas

    all_match_static = []
    for i in range(len(match_ids)):
        match_data = match_datas[i]
        
        if match_data is None:
            continue  # match_datas[i]가 None인 경우 건너뜁니다.

        match_static = pd.json_normalize(match_data['included'], sep='_')
        all_match_static.append(match_static)

        # GameMode와 MapName 정보를 가져와서 DataFrame에 추가합니다.
        matchId = match_data['data']['id']
        game_mode = match_data['data']['attributes']['gameMode']
        map_name = match_data['data']['attributes']['mapName']

        # match_static DataFrame에 새로운 컬럼을 추가합니다.
        match_static['GameMode'] = game_mode
        match_static['MapName'] = map_name
        match_static['matchId'] = matchId



    result = pd.concat(all_match_static, ignore_index=True)
    result.columns = result.columns.str.replace('attributes_stats_', '')
    attributes_URLS = result[result['type'] == 'asset']['attributes_URL'].tolist()


    @st.cache_resource
    def get_log_details():
        response2 = requests.get(attributes_URLS[0], headers=headers)
        log = response2.json()
        log_df = pd.json_normalize(log[1:])
        return log_df

    log_df = get_log_details()
    st.write(log_df)



    with st.container():
        st.subheader('''
                     반동과 관련한 지표                   
                     ''')
        st.write('''
                 ### 부위별 hit을 통한 반동체크 
                 * 근접전 500m 미만의 거리에서 1초동안 5발이상 사용한 경우의 데이터
                 * 부위별로 어느위치를 많이 맞췄는지 비율을 구할 수 있다.
                 * 10초이내에 멀티킬을 달성한 경우
                 ### 초탄 이후의 hit을 통한 반동체크
                 * 두 번째 탄을 맞췄는지 확인
                 * 만약 맞췄다면, 두 번째 탄과 첫 번째 탄의 부위 차이
                
                > 그렇다면 필요한 데이터는 1초동안 5shot + 2번 이상 hit + 500m 미만 
                > 똑같은 부위를 많이 맞출 수 록 반동이 적다고 볼 수 있을것 이다.
                > 하지만 초탄기준을 어떻게 봐야하는가.. 여러 
                 ''')

        # st.write(result_df[['_Ds','_T','attacker.name','weapon.itemId','fireWeaponStackCount','LegShot','ArmShot','TorsoShot','distance']])

if hasattr(st.session_state, 'merged_df'):
    merged_df = st.session_state.merged_df
    merged_df['Date'] = pd.to_datetime(merged_df['_Ds']).dt.strftime('%Y-%m-%d')
    merged_df['Miss'] = merged_df['shot'] - merged_df['hit']


    # Define the minimum and maximum dates correctly
    min_date = datetime.date(2024, 6, 1)
    max_date = datetime.date(2024, 7, 20)

    # Set the default value within the range of min_date and max_date
    default_date = datetime.date(2024, 6, 10)  # This is an example; set it according to your needs

    d = st.date_input(
        "date",                       
        (min_date, max_date),  # Default value within the range
        min_value=min_date,  # Minimum date
        max_value=max_date,  # Maximum date
        format="YYYY.MM.DD"
    )

    start_d = str(d[0])
    end_d = str(max_date)

    date_mask = (merged_df['Date'] >= start_d) & (merged_df['Date'] <= end_d) # date로 지정된 값들만 
    merged_df = merged_df.loc[date_mask]

    # Gun Option
    c1,c2 =st.columns([1,3])
    with c1:

        gun_type = merged_df['weapon.genre'].unique().tolist()
        gun_type_option = st.selectbox('GunGenre', gun_type)


        filtered_df = merged_df[
            # (merged_df['distanceMean'] >= 0) &
            (merged_df['distanceMean'] < 65) &
            (merged_df['shot'] >= 10) &
            (merged_df['weapon.genre'].isin([gun_type_option]))
            ] # 머신건 기준, 스나이퍼의 경우 초당 5발 이상 쓰는경우 거의없다..



    with c2:
        # 1000발 이상 사용된 총만가져옵니다.
        shot_cnt = filtered_df.groupby(['weapon.itemId'],observed=False).agg({'shot':'sum','hit':'sum'}).reset_index()
        gun_under_1000 = shot_cnt[shot_cnt['shot'] > 1000]['weapon.itemId'].unique().tolist()    
        gun_option = st.multiselect('GunName', gun_under_1000, gun_under_1000[:3])
        
    
        group_static = filtered_df[filtered_df['weapon.itemId'].isin(gun_option)].groupby(['weapon.itemId','distance_category'],observed=False).agg(
                        shot = pd.NamedAgg(column='shot', aggfunc='sum'),
                        hit = pd.NamedAgg(column='hit', aggfunc='sum'),
                        HeadShot = pd.NamedAgg(column='HeadShot', aggfunc='sum'),
                        ArmShot = pd.NamedAgg(column='ArmShot', aggfunc='sum'),
                        LegShot = pd.NamedAgg(column='LegShot', aggfunc='sum'),
                        PelvisShot = pd.NamedAgg(column='PelvisShot', aggfunc='sum'),
                        TorsoShot = pd.NamedAgg(column='TorsoShot', aggfunc='sum'),
                        ratio = pd.NamedAgg(column='ratio', aggfunc='mean'),
                                        
                        ).fillna(0).reset_index()

        group_static['ratio'] = group_static['ratio'].astype(int)
        group_statics = group_static[group_static['shot'] > 100]


    def to_nivo():
        gun = []
        for itemId, group in group_statics.groupby('weapon.itemId'):
            if len(group) > 0:
                
                weapon_itemId = group.iloc[0]['weapon.itemId']
                ratio = group.iloc[-1]['ratio']

                gun.append({
                    'id': weapon_itemId,
                    'data' : [{'x': distance_category, 'y': ratio} for distance_category, ratio in zip(group['distance_category'], group['ratio'])],
                })
        return gun
    gun = to_nivo()

    with st.container():
        col1,col2 = st.columns([5,2])
        with col1:
            st.markdown(f'''### Data By GunType''')
            st.markdown('''
                        > * 10초단위로 10발 이상 사용한 총
                        > * 거리별 100발 이상의 데이터가 있는 총기를 기준으로 집계되었습니다.
                            
                            ''')
            # st.write(group_statics)
            # st.caption(''' 거리별 100발 이상 사용한 총기만 집계됩니다. ''' )
            
            with elements("Gun_shot_hit_ratio"):
                layout = [
                    dashboard.Item("item_1", 0, 0, 9, 3),
                    dashboard.Item("item_2", 9, 0, 3, 3),

                ]
                card_sx = {"background-color":"#181819","borderRadius": "10px"}
                with dashboard.Grid(layout):
                    mui.Box( # 재생목록별 전체 조회수 증가량
                        nivo.Line(
                            data= gun,
                            margin={'top': 40, 'right': 30, 'bottom': 90, 'left': 90},
                            xScale={'type': 'point',
                                    },
                            curve="cardinal", #cardinal
                            axisTop=None,
                            axisRight=None,
                            colors= {'scheme': 'nivo'},
                            enableGridX = False,
                            enableGridY = False,
                            enableArea = True,
                            areaOpacity = 0.1,
                            lineWidth=3,
                            pointSize=3,
                            pointColor='white',
                            pointBorderWidth=0.5,
                            pointBorderColor={'from': 'serieColor'},
                            pointLabelYOffset=-12,
                            useMesh=True,
                            legends=[
                                        {
                                        'anchor': 'bottom-left',
                                        'direction': 'column',
                                        'justify': False,
                                        'translateX': 10,
                                        'translateY': -30,
                                        "itemTextColor": "white",
                                        'itemsSpacing': 0,
                                        'itemDirection': 'left-to-right',
                                        'itemWidth': 80,
                                        'itemHeight': 15,
                                        'itemOpacity': 0.75,
                                        'symbolSize': 12,
                                        'symbolShape': 'circle',
                                        'symbolBorderColor': 'rgba(0, 0, 0, .5)',
                                        'effects': [
                                                {
                                                'on': 'hover',
                                                'style': {
                                                    'itemBackground': 'rgba(0, 0, 0, .03)',
                                                    'itemOpacity': 1
                                                    }
                                                }
                                            ]
                                        }
                                    ],                            

                            axisLeft={
                                'tickSize': 2,
                                'tickPadding': 3,
                                'tickRotation': 0,
                                'legend': 'Ratio',
                                'legendOffset': -50,
                                'legendPosition': 'middle'
                            },
                            axisBottom={
                                'tickSize': 2,
                                'tickPadding': 3,
                                'tickRotation': 0,
                                'legend': 'Distance',
                                'legendOffset': 50,
                                'legendPosition': 'middle'
                            },
                            theme={
                                    # "background-color": "rgba(158, 60, 74, 0.2)",
                                    "textColor": "white",
                                    "tooltip": {
                                        "container": {
                                            "background": "#3a3c4a",
                                            "color": "white",
                                        }
                                    }
                                },
                            animate= False),key="item_1",sx=card_sx) 

                    # mui.Card('Weekly Weapon Rank',key='item_2')
        with col2:
            if hasattr(st.session_state, 'merged_df'):
                recoil_df = st.session_state.merged_df
                recoil_df['Miss'] = recoil_df['shot'] - recoil_df['hit']

                with st.container():
                    # st.write('''
                    #         ### 부위별 hit을 통한 반동체크 
                    #         * 근접전 20 미만의 거리에서 5초동안 10발이상 사용한 경우의 데이터 기준으로 집계하였습니다.
                    #         * 부위별로 좌표를 정의하여 초탄과의 거리차이를 구하고 총기별로 평균을 구해 반동을 계산했습니다.
                    #         * 100발 이상 사용된 총기의 기준으로 집계하였습니다. 
                    #         > 결론적으로, 같은 부위를 자주 맞춘 경우 반동이 적다고 볼 수 있습니다. 부위별로 랜덤으로 좌표가 생성되므로 한계점이 있습니다.                 
                    #         ''')

                    st.subheader(''' 
                                 총기별 반동 분포
                                 ''')

                    st.markdown('''
                                * 20 미만의 거리에서 5초동안 10발이상 사용한 경우                 
                                * 부위별로 좌표를 정의하여 초탄과의 거리차이를 구하고 총기별로 평균을 구해 반동을 계산
                                ''')
                        
                    

                    filtered_df2 = recoil_df[
                        (recoil_df['victim.name'].notna()) &
                        (recoil_df['distanceMean'] < 20) &
                        (recoil_df['shot'] >= 10) &   
                        (recoil_df['weapon.genre'].isin([gun_type_option]))
                        ] 


                    # 부위별 좌표 랜덤생성
                    @st.cache_resource
                    def to_recoil(filtered_df2):
                        hit_locations = {
                            'HeadShot': [(40, 75, 240, 280)],
                            'TorsoShot':[(30, 90, 175, 240)] ,
                            'ArmShot': [(0,30,230,140),(90,120,230,140)],
                            'PelvisShot': [(30,90,150,175)],
                            'LegShot': [(30,90,10, 150)],
                            'Miss' : [(0, 20, 10, 120),
                                (95, 120, 10, 120),
                                (80, 120, 250, 300),
                                (0, 40, 250, 300),
                                ]

                        }
                        def generate_random_coordinates(hit_location_ranges):
                            x1, x2, y1, y2 = hit_location_ranges
                            x = random.uniform(x1, x2)
                            y = random.uniform(y1, y2)
                            return {'x': x, 'y': y}
                        
                        def calculate_coordinates(row):
                            coordinates = []
                            for hit_type, ranges in hit_locations.items():
                                num_hits = row[hit_type]
                                for _ in range(num_hits):
                                    coord = generate_random_coordinates(ranges[0])  # Assuming only one range tuple per hit_type
                                    coordinates.append(coord)
                            return coordinates

                        # 랜덤 생성된 좌표들의 차이를 구한다음 평균을 구한다. -> 반동지표
                        def calculate_recoil(row):
                            recoil_values = []
                            prev_x = None
                            prev_y = None
                            for coord in row['hit_coordinates']:
                                x = coord['x']
                                y = coord['y']
                                if prev_x is not None and prev_y is not None:
                                    # Calculate Euclidean distance between consecutive shots
                                    recoil = np.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                                    recoil_values.append(recoil)
                                prev_x = x
                                prev_y = y
                            # Return mean recoil value
                            if recoil_values:
                                return np.mean(recoil_values)
                            else:
                                return np.nan

                            return recoil_values

                        filtered_df2['hit_coordinates'] = filtered_df2.apply(calculate_coordinates, axis=1)
                        filtered_df2['recoil'] = filtered_df2.apply(calculate_recoil, axis=1)


                        recoil_static = filtered_df2.groupby(['weapon.genre','weapon.itemId']).agg(
                            recoil = pd.NamedAgg(column='recoil',aggfunc='mean'),
                            shot = pd.NamedAgg(column='shot',aggfunc='sum'),
                            hit = pd.NamedAgg(column='hit',aggfunc='sum'),
                        ).sort_values(by=['weapon.genre','recoil'],ascending=False).reset_index() # [AR_df['ratio']>40]

                        recoil = recoil_static[recoil_static['hit'] > 100]
                        recoil['recoil'] = recoil['recoil'].round()

                        # 'recoil' 값을 정규화 (0 ~ 100)
                        # scaler = MinMaxScaler(feature_range=(10, 90))
                        # recoil['recoil'] = scaler.fit_transform(recoil[['recoil']]).round()
                        return filtered_df2, recoil


                    filtered_df2, recoil = to_recoil(filtered_df2)       
                    keys = recoil['weapon.itemId'].tolist()
                    recoil_dict = recoil.to_dict('records')


                    # 20m 미만 + 어그
                    aug = filtered_df2[(filtered_df2['weapon.itemId'] == 'Item_Weapon_ACE32_C')]

                    # Matplotlib 그래프 생성
                    fig, ax = plt.subplots()

                    # 히스토그램 생성
                    counts, bins, patches = ax.hist(aug['recoil'], bins=20, alpha=1, color='#92A7C4', edgecolor='black', label='aug')

                    # 축 및 레이블 설정
                    ax.set_xlabel('Recoil', color='white')
                    ax.set_title('AUG Recoil Distribution', color='white')

                    # 눈금 및 눈금 레이블 색상 변경
                    ax.tick_params(colors='white', which='both')

                    # 배경색 설정
                    ax.set_facecolor('black')  # 축 배경색 
                    fig.patch.set_facecolor('black')  # 그림 배경색 

                    st.pyplot(fig)



                    
                    # with elements("Gun_recoil_Top"):
                    #         layout = [
                    #             dashboard.Item("item_1", 0, 0, 9, 3),

                    #         ]
                    #         card_sx = {"background-color":"#181819","borderRadius": "10px"}
                    #         with dashboard.Grid(layout):                                            
                    #             nivo.Bar(
                    #                 data=recoil_dict,
                    #                 keys=["recoil"],  # 막대 그래프의 그룹을 구분하는 속성
                    #                 indexBy='weapon.itemId',  # x축에 표시할 속성

                    #                 margin={"top": 0, "right": 0, "bottom": 0, "left": 150},
                    #                 padding={0.4},
                    #                 layout="horizontal",

                    #                 valueScale={ "type" : 'linear' },
                    #                 indexScale={ "type": 'band', "round": 'true'},
                    #                 borderRadius={5},
                    #                 colors=["#3357FF"],
                    #                 colorBy="indexValue",                 

                    #                 innerRadius=0.3,
                    #                 padAngle=0.5,
                    #                 activeOuterRadiusOffset=8,
                    #                 enableGridY= False,

                    #                 # labelSkipWidth={},
                    #                 # labelSkipHeight={36},
                    #                 axisBottom=False,
                    #                 theme={
                    #                         # "background": "black",
                    #                         "textColor": "white",
                    #                         "tooltip": {
                    #                             "container": {
                    #                                 "background": "#3a3c4a",
                    #                                 "color": "white",
                    #                             }
                    #                         }
                    #                     }                         
                    #                 , key="item_1", elevation=0 , sx=card_sx)        

                        


if hasattr(st.session_state, 'item_score_df'):
    item_score_df = st.session_state.item_score_df
    st.write(item_score_df)
 
 
 

if hasattr(st.session_state, 'streak_df'):
    streak_df = st.session_state.streak_df
    st.write(streak_df)