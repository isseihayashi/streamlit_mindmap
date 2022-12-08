from re import sub
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import os
import datetime
import subprocess
import pyperclip
from gensim.models import KeyedVectors
import gensim
from zipfile import ZipFile
import tempfile
import os, glob
from pymagnitude import Magnitude, MagnitudeUtils
import matplotlib.font_manager 

# NLP_PATH = r"\\sd-ai-cpu01\k220415243\WORK\synonym.exe"

def main():
    
    # raise (print(matplotlib.font_manager.findSystemFonts()))
    # ------------------------------- サイドバー -------------------------------
    input_text_main = st.sidebar.text_area('入力画面',height=350, key='input')
    

    st.sidebar.download_button(
        label="保存",
        data=input_text_main,
        file_name=f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
    )

    input_text_search = st.sidebar.text_input('類似単語')
    # 初回だけLocalにモデルをDLしてる？
    model = Magnitude(MagnitudeUtils.download_model("chive-1.1-mc90-aunit", remote_path="https://sudachi.s3-ap-northeast-1.amazonaws.com/chive/"))

    if st.sidebar.button(label='SEARCH'):
        if input_text_search == "":
            st.error("検索単語を入力して下さい")
        else:
            print('Begin Search')
            from subprocess import PIPE
            # reserch_result = subprocess.run(NLP_PATH +" "+ input_text_search, shell=True, stdout=PIPE, stderr=PIPE, text=True)
            reserch_result = model.most_similar(input_text_search, topn=5)
            result_list = reserch_result
            st.session_state.result_word = [result[0] for result in result_list]

    input_divine_word = st.sidebar.selectbox('区切り文字', ['.', ',', ' ', '_', '-', '/', '、', '。'])
    input_upload = st.sidebar.file_uploader("ファイルアップロード", type='txt')

    if type(input_upload) == type(None):
        pass
    else:
        input_text_main = input_upload.getvalue().decode(encoding='utf-8')

    width = st.sidebar.slider("plot width", 1.0, 25., 10., step=1.0)
    height = st.sidebar.slider("plot height", 1.0, 25., 8., step=1.0)
    
    # ------------------------------- メイン -------------------------------
    '''
    ### 発想支援ツール
    '''
    # グラフ用意
    words = input_text_main.split(sep='\n')
    raw_words = []
    edge_list = []
    replace_keyword = input_divine_word

    #自分とカウントが差異1のモノが来たら繋げる
    #同値のものがきたら閉じる
    for index, word in enumerate(words):
        
        raw_words.append(word.replace(replace_keyword, ''))
        current_level = word.count(replace_keyword)
        
        # search 1step down level below
        for word_obj in words[index+1:]:
            level_obj = word_obj.count(replace_keyword)
            dif_level = level_obj - current_level

            if dif_level == 0:
                break

            elif dif_level == 1:
                edge_list.append((word.replace(replace_keyword,''), word_obj.replace(replace_keyword,'')))

    try:
        pre_input_text_main = st.session_state.text_main
        is_changed = input_text_main != pre_input_text_main

    except Exception as e:
        is_changed = True
        print(e)

    if is_changed:
        # Graphオブジェクトの作成
        fig = plt.figure(figsize=(width, height))
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)

        G = nx.Graph()
        # nodeデータの追加
        G.add_nodes_from(raw_words) 
        # edgeデータの追加
        G.add_edges_from(edge_list)
        # ネットワークの可視化
        pos = nx.spring_layout(G, k=0.9)

        # グラフ描画設定
        nx.draw_networkx_nodes(G, pos, node_size=1500, node_color = "#f5eeff")
        # FIXME Streamlit cloud(Sharing)で日本語が表示されない(□になる)
        # ローカル環境では表示できているので、サーバー上にフォントが存在しないことが原因だと思われる
        # 'packages.txt'内に記述することでフォントのDLを実現しているがなぜか存在しないと判定される
        # 
        nx.draw_networkx_labels(G, pos, font_family='fonts-japanese-mincho')
        nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color='#0f0f0f')

    else:
        fig = st.session_state.fig
        pass

    # グラフ描画
    st.pyplot(fig)

    st.session_state.text_main = input_text_main
    st.session_state.fig = fig

    # 類似単語検索結果

    '''
    類似単語検索結果
    '''

    try:
        for index, result in enumerate(st.session_state.result_word[:5]):
            col = st.columns(2)
            col[0].write(result)
            if col[1].button('COPY', key=index):
                pyperclip.copy(result.replace('[','').replace(']',''))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
