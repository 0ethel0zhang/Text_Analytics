import re
import numpy as np

print("Program started")

###initialization
# compile all punctuations
punc = re.compile("[^"+"|".join(list('!"#$%&\'()*+,--./:;<=>?@\[\\]^_`{|}~'))+"]")

###Functions
def preprocess(file):
    """ Read and process lines into a list
    :param file: (str) path to and the name of the file
    :return: (list) a list of lines
    """
    # read doc
    with open(file, 'r', encoding='UTF-8', errors='ignore') as f:
        doc = f.readlines()
        lines = []
        for x in doc:
            lines.append(x.lower().strip(""))
        del doc

    # process all punctuations and extra white space
    lines_np = ["".join(re.findall(punc, x)) for x in lines]
    lines_np_one = [x.strip().replace("  ", " ") for x in lines_np]

    # process the digits/ranks with digits out
    lines_np_nd = []
    for x in lines_np_one:
        if len(re.findall("\d+", x)) > 0:
            new = x
            for digits in re.findall(r"\b(\d+(th|st|nd)?)\b", x):
                new = re.sub(re.compile(r"\b" + digits[0] + r"\b"), "NUMBER", new)
            lines_np_nd.append(new)
        else:
            lines_np_nd.append(x)

    return lines_np_nd

def ngrams_words(lst, returnwords = True, n = 2):
    """process lines of sentences into ngrams"""
    # n-grams init
    ngrams = []
    # if each word is needed
    if returnwords:
        words_all = []
    else:
        words_all = None
    #create n-grams
    for sent in lst:
        words = sent.split(' ')
        if returnwords:
            words_all += words
        length = len(words)
        for i in range(0, length - n + 1):
            n_gram = ' '.join(words[i : i + n])
            ngrams.append(n_gram)
    return ngrams, words_all

def ngrams_process(ngrams, words_all, normal=True, addone=True, turing=True):
    """process bigrams into probabilities"""
    # vocabulary
    vocab = np.unique(words_all).tolist()
    vocab.remove('')
    vocab.remove(']')

    # word dict
    vocab_dic = dict(zip(vocab, range(len(vocab))))
    vocab_dic_r = dict(zip(range(len(vocab)), vocab))

    # count table
    ngram_cnt = np.zeros((len(vocab), len(vocab)), dtype="int")
    for ngram in ngrams:
        words = ngram.split(" ")
        try:
            ngram_cnt[vocab_dic[words[0]], vocab_dic[words[1]]] += 1
        except:
            next

    # prob table
    if normal:
        ngram_p = ngram_cnt / ngram_cnt.sum()
    if addone:
        ngram_cnt_t = ngram_cnt + 1
        ngram_p_ao = ngram_cnt_t / ngram_cnt_t.sum()
    if turing:
        ngram_cnt_dict = {}
        u = np.unique(ngram_cnt)
        for h in u:
            ngram_cnt_dict[h] = len(np.where(ngram_cnt == h)[0])

    return vocab, vocab_dic, vocab_dic_r, ngram_cnt, ngram_p, ngram_p_ao, ngram_cnt_dict

###Read training & test files
# english train
eng_np_nd = preprocess("LangId.train.English")
# italian train
it_np_nd = preprocess("LangId.train.Italian")
# french train
fr_np_nd = preprocess("LangId.train.French")
# test
test_np_nd = preprocess("LangId.test")

### words n-gram Training

# English

ngram_eng, words_eng = ngrams_words(eng_np_nd)

vocab_eng, vocab_eng_dic, vocab_eng_dic_r, ngram_cnt, ngram_eng_p, ngram_eng_ao, ngram_eng_gt = ngrams_process(
    ngram_eng, words_eng)

# Italian

ngram_it, words_it = ngrams_words(it_np_nd)

vocab_it, vocab_it_dic, vocab_it_dic_r, ngram_it_cnt, ngram_it_p, ngram_it_ao, ngram_it_gt = ngrams_process(
    ngram_it, words_it)

# French

ngram_fr, words_fr = ngrams_words(fr_np_nd)

vocab_fr, vocab_fr_dic, vocab_fr_dic_r, ngram_fr_cnt, ngram_fr_p, ngram_fr_ao, ngram_fr_gt = ngrams_process(
    ngram_fr, words_fr)

print("Trained letter bigram model")

### Words bi-gram Test

def keepLines(lst, n=2):
    """process as ngrams with lines preserved"""
    # n-grams init
    lines = {}

    for l in range(len(lst)):
        words = lst[l].split(" ")
        n_grams = []
        length = len(words)
        for i in range(0, length - n + 1):
            n_gram = ' '.join(words[i: i + n])
            n_grams.append(n_gram)

        lines[l] = n_grams

    return lines

# test processing
test_dict = keepLines(test_np_nd)

ngram_test, words_test = ngrams_words(test_np_nd)

# prep dictionaries for processing
dicts = dict(zip(["english","french","italian"],
                 [[vocab_eng_dic, ngram_eng_p, ngram_eng_ao, ngram_eng_gt, ngram_cnt],
                  [vocab_fr_dic, ngram_fr_p, ngram_fr_ao, ngram_fr_gt, ngram_fr_cnt],
                  [vocab_it_dic, ngram_it_p, ngram_it_ao, ngram_it_gt, ngram_it_cnt]]))

def likeliness(ngram, lg = "english", smoothing=None):
    """bigram likehood"""
    words = ngram.split(" ")
    lead = words[0]
    follow = words[1]
    vocab_dic = dicts[lg][0]
    #nothing or add-one only (good-turing seperated)
    if smoothing == None:
        ngram_p = dicts[lg][1]
    if smoothing == "add-one":
        ngram_p = dicts[lg][2]
    # check p
    if lead in vocab_dic.keys():
        if follow in vocab_dic.keys():
            p_sub = ngram_p[vocab_dic[lead], vocab_dic[follow]]
            if p_sub == 0:
                p_sub = 1e-100
        else:
            p_sub = 1e-100
    else:
        p_sub = 1e-100
    return np.log(p_sub)

def whatLg(test_dict, smoothing=None):
    """total probability for each line"""
    p_lines = {}
    for k, v in test_dict.items():
        # english
        eng_prob = 1e-100
        for ngram in v:
            if smoothing == "good-turing":
                eng_prob += turing_likeliness(ngram)
            else:
                eng_prob += likeliness(ngram, smoothing=smoothing)

        # french
        fr_prob = 1e-100
        for ngram in v:
            if smoothing == "good-turing":
                fr_prob += turing_likeliness(ngram, "french")
            else:
                fr_prob += likeliness(ngram, "french", smoothing=smoothing)

        # italian
        it_prob = 1e-100
        for ngram in v:
            if smoothing == "good-turing":
                it_prob += turing_likeliness(ngram, "italian")
            else:
                it_prob += likeliness(ngram, "italian", smoothing=smoothing)

        players = {'English': eng_prob, 'French': fr_prob, 'Italian': it_prob}
        winner = max(players, key=players.get)
        p_lines[k] = winner

    return p_lines

# run add-one smoothing
ao_lines = whatLg(test_dict, smoothing="add-one")

print("Prediction made")

# write out solution
with open("wordLangId.out", "w") as f:
    for k, v in ao_lines.items():
        f.writelines(" ".join([str(k+1), v, "\n"]))
    f.close()

print("Find result in wordLangId.out")
