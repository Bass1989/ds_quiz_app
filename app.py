import streamlit as st
import pandas as pd
import random  

# ページの設定
st.set_page_config(page_title="DS検定クイズ", layout="centered")

# CSSでデザイン調整（見やすくする + スマホ対策）
st.markdown("""
    <style>
    /* === 既存の設定 === */
    .stRadio label {font-size: 20px !important;}
    .explanation {background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 20px;}

    /* === 追加設定：上部の余白を削る === */
    .block-container {
        padding-top: 1rem;   /* 上の隙間を小さくする */
        padding-bottom: 5rem;
    }

    /* === 追加設定：スマホ（画面幅600px以下）の時だけタイトルを小さく === */
    @media (max-width: 600px) {
        h1 {
            font-size: 1.5rem !important; /* タイトル文字サイズを小さく */
        }
    }
    </style>
    """, unsafe_allow_html=True)

# タイトル
st.title("🎓 DS検定クイズ")
# st.caption("第5章：ビジネス課題の解決フロー (問1〜8)")

# データの読み込み
@st.cache_data
def load_data():
    # CSVファイルを読み込む
    try:
        return pd.read_csv("quiz_data.csv")
    except FileNotFoundError:
        st.error("エラー: 'quiz_data.csv' が見つかりません。同じフォルダに置いてください。")
        return pd.DataFrame()

df = load_data()

# セッション状態の初期化
if 'shuffled_indices' not in st.session_state:
    # 0から問題数-1までの数字リストを作ってシャッフルする
    indices = list(range(len(df)))
    random.shuffle(indices)
    st.session_state.shuffled_indices = indices
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'show_explanation' not in st.session_state:
    st.session_state.show_explanation = False
if 'user_answer' not in st.session_state:
    st.session_state.user_answer = None

# クイズが終了したかチェック
if not df.empty and st.session_state.current_q_index < len(df):
    # シャッフルされたリストの中から、現在の順番に対応するインデックスを取り出す
    original_index = st.session_state.shuffled_indices[st.session_state.current_q_index]
    # そのインデックスの行（問題）を取得
    row = df.iloc[original_index]

    # 進捗バー
    progress = (st.session_state.current_q_index + 1) / len(df)
    st.progress(progress)
    st.write(f"**第 {st.session_state.current_q_index + 1} 問** / 全 {len(df)} 問")

    # 問題文の表示
    q_text = row['question']  
    # 1. 「適切でない」を太字にする
    q_text = q_text.replace("適切でない", "**適切でない**")
    q_text = q_text.replace("不適切", "**不適切**")
    # 2. <br>タグを、Markdownの改行コード（半角スペース2つ + 改行）に置換する
    q_text = q_text.replace("<br>", "  \n")
    # 表示する
    st.write(q_text)

    # 選択肢のリスト作成
    options = {
        "A": row['option_a'],
        "B": row['option_b'],
        "C": row['option_c'],
        "D": row['option_d']
    }

    # ラジオボタンで回答を選択（キーにindexを含めてリセットさせる）
    choice = st.radio(
        "選択肢を選んでください:",
        options.keys(),
        format_func=lambda x: f"{x}. {options[x]}",
        key=f"radio_{st.session_state.current_q_index}",
        disabled=st.session_state.show_explanation, # 解説表示中は変更不可
        label_visibility="collapsed" 
    )

    # 「回答する」ボタン
    if not st.session_state.show_explanation:
        if st.button("回答する", type="primary"):
            st.session_state.user_answer = choice
            st.session_state.show_explanation = True
            
            # 正解ならスコア加算
            if choice == row['correct_answer']:
                st.session_state.score += 1
            
            st.rerun()

    # 解説の表示（回答ボタンが押された後）
    if st.session_state.show_explanation:
        correct = row['correct_answer']
        user = st.session_state.user_answer
        
        if user == correct:
            st.success(f"✅ 正解！ (答え: {correct})")
        else:
            st.error(f"❌ 不正解... (あなたの回答: {user} / 正解: {correct})")
        
        # 解説文
        st.markdown(f"<div class='explanation'><b>📝 解説:</b><br>{row['explanation']}</div>", unsafe_allow_html=True)
        
        # 「次の問題へ」ボタン
        if st.button("次の問題へ"):
            st.session_state.current_q_index += 1
            st.session_state.show_explanation = False
            st.session_state.user_answer = None
            st.rerun()

elif not df.empty:
    # 全問終了時の画面
    st.balloons()
    st.success("🎉 お疲れ様でした！全問終了です。")
    
    score = st.session_state.score
    total = len(df)
    st.metric(label="最終スコア", value=f"{score} / {total} 点", delta=f"{int(score/total*100)}%")
    
    if st.button("もう一度挑戦する"):
            # セッションをクリアして再読み込み（これでまたシャッフルされます）
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()