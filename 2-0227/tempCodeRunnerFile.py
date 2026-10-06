def find_word_indices(lyrics: str, target_word: str) -> list:
    """
    分析歌詞，找出指定單字在整首歌詞中所有出現的位置（字元索引），
    並將這些位置儲存在 list 中回傳。若未出現則回傳空 list。
    """
    indices = []
    # 轉換成小寫以進行不分大小寫的搜尋
    lower_lyrics = lyrics.lower()
    lower_target = target_word.lower()
    
    start_idx = 0
    while True:
        idx = lower_lyrics.find(lower_target, start_idx)
        if idx == -1:
            break
        indices.append(idx)
        # 移動起始搜尋位置，避免重複計算同一個
        start_idx = idx + len(lower_target)
        
    return indices

# 1. 在此放入您的歌詞內容（此處以短範例示意）
lyrics_content = """
… When you're weary, feeling small,
When tears are in your eyes, I will dry them all;
I'm on your side. When times get rough
And friends just can't be found,
Like a bridge over troubled water
I will lay me down.
Like a bridge over troubled water
I will lay me down.
… When you're down and out,
When you're on the street,
When evening falls so hard
I will comfort you.
I'll take your part.
When darkness comes
And pain is all around,
Like a bridge over troubled water
I will lay me down.
Like a bridge over troubled water
I will lay me down.
… Sail on silvergirl,
Sail on by.
Your time has come to shine.
All your dreams are on their way.
See how they shine.
If you need a friend
I'm sailing right behind.
Like a bridge over troubled water
I will ease your mind.
Like a bridge over troubled water
I will ease your mind.

"""

# 2. 指定您想要搜尋的單字（例如 "bridge" 或 "water"）
target = "bridge"

# 3. 執行分析函數
result_indices = find_word_indices(lyrics_content, target)

# 4. 輸出結果
print(f"單字 '{target}' 在歌詞中的所有位置索引：{result_indices}")