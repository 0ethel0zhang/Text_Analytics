import logging
import re
import numpy as np
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

###initialization
# compile all punctuations
punc = re.compile("[^"+"|".join(list('!"#$%&\'()*+,--./:;<=>?@\[\\]^_`{|}~'))+"]")

### Functions
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

def ngrams_process(ngrams, words_all, turing=True):
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

    # count frequency table
    if turing:
        ngram_cnt_dict = {}
        u = np.unique(ngram_cnt)
        for h in u:
            ngram_cnt_dict[h] = len(np.where(ngram_cnt == h)[0])
    else:
        ngram_cnt_dict = None

    return vocab, vocab_dic, vocab_dic_r, ngram_cnt, ngram_cnt_dict

###Read training & test files
# english train
eng_np_nd = preprocess("LangId.train.English")
# italian train
it_np_nd = preprocess("LangId.train.Italian")
# french train
fr_np_nd = preprocess("LangId.train.French")
# test
test_np_nd = preprocess("LangId.test")

print("Read documents")

### words n-gram Training

# English

ngram_eng, words_eng = ngrams_words(eng_np_nd)

vocab_eng, vocab_eng_dic, vocab_eng_dic_r, ngram_cnt, ngram_eng_gt = ngrams_process(
    ngram_eng, words_eng)

# Italian

ngram_it, words_it = ngrams_words(it_np_nd)

vocab_it, vocab_it_dic, vocab_it_dic_r, ngram_it_cnt, ngram_it_gt = ngrams_process(
    ngram_it, words_it)

# French

ngram_fr, words_fr = ngrams_words(fr_np_nd)

vocab_fr, vocab_fr_dic, vocab_fr_dic_r, ngram_fr_cnt, ngram_fr_gt = ngrams_process(
    ngram_fr, words_fr)

print("Trained good turing model")

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

# good turing zeros
def GTzeros(ngram_test, ngram_train, ngram_gt):
    dif = len(set(ngram_test).difference(set(ngram_train)))
    ngram_gt[0] = dif
    return ngram_gt

gt_eng_dif = GTzeros(ngram_test, ngram_eng, ngram_eng_gt)
gt_fr_dif = GTzeros(ngram_test, ngram_fr, ngram_fr_gt)
gt_it_dif = GTzeros(ngram_test, ngram_it, ngram_it_gt)

gt_dicts = dict(zip(["english", "french", "italian"],
                    [[vocab_eng_dic, ngram_cnt, gt_eng_dif],
                     [vocab_fr_dic, ngram_fr_cnt, gt_fr_dif],
                     [vocab_it_dic, ngram_it_cnt, gt_it_dif]]))


def turing_likeliness(ngram, vocab_dic, gt_cnt, gt_cnt_dict):
    """process ngram's good turing likelihood"""
    words = ngram.split(" ")
    lead = words[0]
    follow = words[1]
    
    # check count
    if lead in vocab_dic.keys():
        if follow in vocab_dic.keys():
            cnt_sub = gt_cnt[vocab_dic[lead], vocab_dic[follow]]
        else:
            cnt_sub = 0
    else:
        cnt_sub = 0

    c_ori = gt_cnt_dict[cnt_sub]

    if cnt_sub < max(gt_cnt_dict.keys()):
        for key in sorted(list(gt_cnt_dict.keys()), reverse=True):
            if key > cnt_sub:
                c_plus = gt_cnt_dict[key]
                cnt_sub = key
    else:
        c_plus = cnt_sub
    try:
        p = np.log(cnt_sub * c_plus / c_ori / gt_cnt.sum())
    except:
        p = np.log(1e-100 * c_plus / c_ori / gt_cnt.sum())

    return p

def whatLg(test_dict):
    """total probability for each line"""
    p_lines = {}
    for k, v in test_dict.items():
        # english
        eng_prob = 1e-100
        for ngram in v:
            eng_prob += turing_likeliness(ngram, vocab_dic = gt_dicts["english"][0],
                                              gt_cnt = gt_dicts["english"][1],
                                              gt_cnt_dict = gt_dicts["english"][2])

        # french
        fr_prob = 1e-100
        for ngram in v:
            fr_prob += turing_likeliness(ngram, vocab_dic = gt_dicts["french"][0],
                                              gt_cnt = gt_dicts["french"][1],
                                              gt_cnt_dict = gt_dicts["french"][2])

        # italian
        it_prob = 1e-100
        for ngram in v:
            it_prob += turing_likeliness(ngram, vocab_dic = gt_dicts["italian"][0],
                                              gt_cnt = gt_dicts["italian"][1],
                                              gt_cnt_dict = gt_dicts["italian"][2])

        players = {'English': eng_prob, 'French': fr_prob, 'Italian': it_prob}
        winner = max(players, key=players.get)
        p_lines[k] = winner

        if k%5 == 0:
            logging.info('line {} processed'.format(k))

    return p_lines

# run good turing smoothing
out = whatLg(test_dict)

# write out solution
with open("wordLangId2.out", "w") as f:
    for k, v in out.items():
        f.writelines(" ".join([str(k+1), v, "\n"]))
    f.close()

print("Output saved as wordLangId2.out")
