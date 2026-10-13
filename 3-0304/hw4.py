
lyrics = '''Hello darkness, my old friend
I've come to talk with you again
Because a vision softly creeping
Left its seeds while I was sleeping
And the vision that was planted in my brain
Still remains
Within the sound of silence
In restless dreams, I walked alone
Narrow streets of cobblestone
'Neath the halo of a street lamp
I turned my collar to the cold and damp
When my eyes were stabbed by the flash of a neon light
That split the night
And touched the sound of silence
And in the naked light, I saw
Ten thousand people, maybe more
People talking without speaking
People hearing without listening
People writing songs that voices never shared
And no one dared
Disturb the sound of silence
"Fools" said I, "You do not know
Silence like a cancer grows
Hear my words that I might teach you
Take my arms that I might reach you"
But my words, like silent raindrops fell
And echoed in the wells of silence
And the people bowed and prayed
To the neon god they made
And the sign flashed out its warning
In the words that it was forming
Then the sign said, "The words on the prophets are written on the subway walls
In tenement halls"
And whispered in the sound of silence'''

def count_words(lyrics, target_words):
    # 先把歌詞拆成單字，並忽略大小寫與標點符號
    words = [word.lower() for word in __import__('re').findall(r"[A-Za-z]+", lyrics)]

    # 讓 dictionary 中保留原本指定的 key 形式，並依照大小寫不敏感計數
    target_map = {word.lower(): word for word in target_words}
    counts = {word: 0 for word in target_words}

    for word in words:
        if word in target_map:
            counts[target_map[word]] += 1

    return counts

search_words = ["silence", "People", "neon", "words", "the"]
result = count_words(lyrics, search_words)
print(result)