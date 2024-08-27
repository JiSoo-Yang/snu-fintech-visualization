import pandas as pd
import folium
from folium.plugins import HeatMap
import streamlit as st

# 데이터 불러오기
df = pd.read_csv("교통사고 데이터/12_23_death.csv", encoding='euc-kr')

# '발생년월일시' 컬럼을 10자리로 맞추기 위해 zfill 사용
df['발생년월일시'] = df['발생년월일시'].astype(str).str.zfill(10)

# '발생년월일시'를 datetime 형식으로 변환
df['발생일시'] = pd.to_datetime(df['발생년월일시'], format='%Y%m%d%H', errors='coerce')

# 발생일시가 제대로 변환되지 않은 데이터를 필터링
df = df.dropna(subset=['발생일시'])

# 사망자수와 중상자수를 합산한 사상자수 열 추가
df['사상자수'] = df['사망자수'] + df['중상자수']

# Streamlit 인터페이스 설정
st.title('시간에 따른 사상자 수 변화')

# 모든 발생일시 값을 타임스탬프로 변환
df['발생일시_timestamp'] = df['발생일시'].apply(lambda x: x.timestamp())

# 시간 슬라이더 설정
min_time = int(df['발생일시_timestamp'].min())
max_time = int(df['발생일시_timestamp'].max())

# 시간 슬라이더
selected_time_timestamp = st.slider('시간을 선택하세요', min_value=min_time, max_value=max_time, value=min_time)

# 타임스탬프를 다시 datetime 형식으로 변환
selected_time = pd.to_datetime(selected_time_timestamp, unit='s')

# 선택한 시간 이전의 데이터 필터링
filtered_data = df[df['발생일시'] <= selected_time]

# 지도 생성
map = folium.Map(location=[df['위도'].mean(), df['경도'].mean()], zoom_start=10)

# 사고 데이터를 기반으로 히트맵을 생성
heat_data = [[row['위도'], row['경도'], row['사상자수']] for index, row in filtered_data.iterrows()]
HeatMap(data=heat_data, radius=10, blur=15, max_zoom=1).add_to(map)

# 지도 HTML을 임시 파일로 저장
map.save('map.html')

# Streamlit에서 HTML 파일을 읽어와 표시
st.components.v1.html(open('map.html', 'r').read(), height=500)
