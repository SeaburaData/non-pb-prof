import streamlit as st
import json
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

def load_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def load_data(data_type):
    file_path = 'data/pit.json' if data_type == 'Pitch' else 'data/bat.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        st.error(f"データファイル({file_path})が見つかりません。")
        return None
    except json.JSONDecodeError:
        st.error(f"JSONファイルの形式が正しくありません。")
        return None

def get_options(data, year=None, league=None, team=None):
    if data is None:
        return [], [], [], []
        
    years = list(data.keys())
    
    leagues = []
    if year and year != "Select Year":
        leagues = list(data[year].keys())
    
    teams = []
    if year and year != "Select Year" and league and league != "Select League":
        teams = list(data[year][league].keys())
    
    names = []
    if (year and year != "Select Year" and 
        league and league != "Select League" and 
        team and team != "Select Team"):
        players = data[year][league][team]
        names = [(player["nameJ"], player["nameE"]) for player in players]
    
    return years, leagues, teams, names

def main():
    st.title("non-pb identifier (beta)")
    # 引用元の表示（リンク付き）
    st.subheader('quoted from [bouno05](https://bo-no05.hatenadiary.org/)')

    # CSSファイルの読み込み
    load_css('css/style.css')
    
    # ラジオボタンの追加
    data_type = st.radio(
        "",
        options=['Pitch', 'Bat'],
        horizontal=True
    )
    
    # データの読み込み（選択されたタイプに基づく）
    data = load_data(data_type)
    
    if data is None:
        return
    
    # 年度のプルダウン
    years, _, _, _ = get_options(data)
    selected_year = st.selectbox(
        "",
        options=["Select Year"] + years,
        index=0
    )
    
    # リーグのプルダウン
    _, leagues, _, _ = get_options(data, selected_year)
    selected_league = st.selectbox(
        "",
        options=["Select League"] + leagues,
        index=0
    )
    
    # チームのプルダウン
    _, _, teams, _ = get_options(data, selected_year, selected_league)
    selected_team = st.selectbox(
        "",
        options=["Select Team"] + teams,
        index=0
    )
    
    # 選手名のプルダウン
    _, _, _, names = get_options(data, selected_year, selected_league, selected_team)
    name_options = ["Select Player"] + [f"{name[0]} ({name[1]})" for name in names] if names else []
    selected_name = st.selectbox(
        "",
        options=name_options,
        index=0
    )
    
    # すべての選択が完了しているか確認
    all_selected = (selected_year != "Select Year" and 
                   selected_league != "Select League" and 
                   selected_team != "Select Team" and 
                   selected_name != "Select Player")
    
    # 表示ボタン
    if st.button("Display Profile", disabled=not all_selected):
        # 選手のIDsを取得して表示
        players = data[selected_year][selected_league][selected_team]
        selected_player = None
        for player in players:
            player_full_name = f"{player['nameJ']} ({player['nameE']})"
            if player_full_name == selected_name:
                selected_player = player
                break
        
        if selected_player:
            st.subheader("Player Profile")
            try:
                # 1枚目の画像を処理
                url1 = f"https://drive.google.com/uc?id={selected_player['ids'][0]}"
                response = requests.get(url1)
                image1 = Image.open(BytesIO(response.content))
                st.image(image1, use_container_width=True)
                
                # 2枚目の画像を処理
                url2 = f"https://drive.google.com/uc?id={selected_player['ids'][1]}"
                response = requests.get(url2)
                image2 = Image.open(BytesIO(response.content))
                st.image(image2, use_container_width=True)
                    
            except Exception as e:
                st.error("画像の読み込みに失敗しました。")
                st.error(str(e))

if __name__ == "__main__":
    main()