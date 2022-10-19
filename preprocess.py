from utils.Preprocess import Preprocess
from utils.FindAnswer import FindAnswer
import pickle




sent = "덕성여대 주변 한식 맛집 알려줘!"

f = open("./train_tools/dict/chatbot_dict.bin", "rb")
word_index = pickle.load(f)
f.close()

p = Preprocess(userdic='./utils/user_dic.tsv')
pos = p.pos(sent)

# 전처리
'''
ret = p.get_keywords(pos, without_tag=False)
print(ret)

ret = p.get_keywords(pos, without_tag=True)
print(ret)
'''

keyword = p.get_keywords(pos, without_tag=True)
for word in keyword:
 try:
  print(word, word_index[word])
 except KeyError:
  print(word, word_index['00V'])