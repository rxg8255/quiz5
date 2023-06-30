# from nltk.tokenize import sent_tokenize
# import nltk
import re

# nltk.download('punkt')
text = 'Some sentence. Mr. Holmes...This is a new sentence!And This is another one.. Hi '
proh = 'sentence,Mr'.split(',')
big_regex = re.compile('|'.join(map(re.escape, proh)))
the_message = big_regex.sub("", text)
print(the_message)