from re import sub
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import datetime
from gensim.models import KeyedVectors
from zipfile import ZipFile
from pymagnitude import Magnitude, MagnitudeUtils
from subprocess import PIPE

def main():
    # ------------------------------- サイドバー -------------------------------
    input_text_main = st.sidebar.text_area('入力画面',height=350, key='input')

    st.sidebar.download_button(
        label="保存",
        data=input_text_main,
        file_name=f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
    )
    # 初回だけLocalにモデルをDLしてる？
    model = Magnitude(MagnitudeUtils.download_model("chive-1.1-mc90-aunit", remote_path="https://sudachi.s3-ap-northeast-1.amazonaws.com/chive/"))
    input_divine_word = st.sidebar.selectbox('区切り文字', ['。', '、', '.', ',', ' ', '_', '-', '/'])
    serch_type = st.sidebar.radio('',('類似単語検索', '単語足し算', '単語引き算'))

    if serch_type == '類似単語検索':
        input_text_search = st.sidebar.text_input('類似単語')
        if st.sidebar.button(label='SEARCH', key='search_from_single'):
            if input_text_search == "":
                st.error("検索単語を入力して下さい")
            else:
                result_list = model.most_similar(input_text_search, topn=5)
                st.session_state.result_word = [result[0] for result in result_list]

    if serch_type == '単語足し算':
        word_pos01=st.sidebar.text_input('1つ目の単語', '')
        word_pos02=st.sidebar.text_input('2つ目の単語', '')
        if st.sidebar.button(label='SEARCH', key='sum_words'):
            if word_pos01 == "":
                st.error("検索単語を入力して下さい")
            else:
                result_list = model.most_similar(positive=[word_pos01, word_pos02], topn=5)
                st.session_state.result_word = [result[0] for result in result_list]
    
    if serch_type == '単語引き算':
        word_pos01=st.sidebar.text_input('1つ目の単語', '')
        word_pos02=st.sidebar.text_input('2つ目の単語', '')
        if st.sidebar.button(label='SEARCH', key='neg_words'):
            if word_pos01 == "":
                st.error("検索単語を入力して下さい")
            else:
                result_list = model.most_similar(negative=[word_pos01, word_pos02], topn=5)
                st.session_state.result_word = [result[0] for result in result_list]
    
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

    # マインドマップ描画のために区切り文字を除いた単語リストと関係を表すエッジリストを作成
    for index, word in enumerate(words):
        
        raw_words.append(word.replace(replace_keyword, ''))
        current_level = word.count(replace_keyword)
        
        # 区切り文字の数が1つ多いものを探しつなげる
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

    # input_text_mainが変更されたときのみグラフを生成する(毎回グラフが変更されるのを防ぐため)
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
        # pos = nx.planar_layout(G)
        # グラフ描画設定
        nx.draw_networkx_nodes(G, pos, node_size=1500, node_color = "#f5eeff")
        nx.draw_networkx_labels(G, pos, font_family='IPAexGothic')
        nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color='#0f0f0f')

    else:
        fig = st.session_state.fig
        pass

    # グラフ描画
    st.pyplot(fig)
    st.session_state.text_main = input_text_main
    st.session_state.fig = fig

    '''
    検索結果
    '''
    try:
        for index, result in enumerate(st.session_state.result_word[:5]):
            col = st.columns(2)
            col[0].write(result)
            
            # if col[1].button('COPY', key=index):
            #     pyperclip.copy(result.replace('[','').replace(']',''))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
