string1 = "I'm a lumberjack, and I'm okay."
string2 = "I sleep all night and I work all day."

# 分別為兩個不同的字串找出 'I' 的索引位置
indices1 = [i for i, char in enumerate(string1) if char == 'I']
indices2 = [i for i, char in enumerate(string2) if char == 'I']

print(f"string1 中 'I' 的位子：{indices1}")
print(f"string2 中 'I' 的位子：{indices2}")
print(f"Total number of 'I' in string1: {len(indices1)}")
print(f"Total number of 'I' in string2: {len(indices2)}")