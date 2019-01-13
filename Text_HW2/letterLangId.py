import re
import numpy as np

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


def l_keepLines(lst, n=2):
    """Create bigrams of letters from test document, while preserving the lines"""
    # n-grams init
    lines = {}
    # get each letter
    letters_all = []

    for l in range(len(lst)):
        line = lst[l].replace("NUMBER", "N")
        words = line.split(" ")
        nletters = []
        for word in words:
            word += " "
            length = len(word)
            for i in range(0, length - n + 1):
                n_gram = word[i: i + n]
                try:  # not getting numbers into the vocabulary
                    int(word[i])
                except:
                    nletters.append(n_gram)
                    if word[i] not in letters_all:
                        if i % 2 == 0:
                            letters_all.append(word[i])

        lines[l] = nletters

    return lines, letters_all

def ngrams_letters(lst, returnletters = True, n = 2):
    """Batch process documents into bigram letters"""
    nletters = []
    letter = []
    for line in lst:
        line = line.replace("NUMBER", "N")
        words = line.split(" ")
        for word in words:
            length = len(word)
            for i in range(0, length - n + 1):
                n_gram = word[i : i + n]
                try:
                    int(word[i])
                except:
                    nletters.append(n_gram)
                    if word[i] not in letter:
                        letter.append(word[i])
            if length > 2:
                try: # not getting numbers into the vocabulary
                    int(word[length -1])
                except:
                    if word[length -1] not in letter:
                        letter.append(word[length - 1])
    return nletters, letter

def nletters_process(nletters, letters, normal=True, addone=True):
    """Process ngram letters for probability analysis"""
    # vocabulary
    vocab = np.unique(letters).tolist()

    # word dict
    vocab_dic = dict(zip(vocab, range(len(vocab))))
    vocab_dic_r = dict(zip(range(len(vocab)), vocab))

    # count table
    ngram_cnt = np.zeros((len(vocab), len(vocab)), dtype="int")
    for letter in nletters:
        try:
            ngram_cnt[vocab_dic[letter[0]], vocab_dic[letter[1]]] += 1
        except:
            next

    # prob table
    if normal:
        ngram_p = ngram_cnt / ngram_cnt.sum()
    if addone:
        ngram_cnt_t = ngram_cnt + 1
        ngram_p_ao = ngram_cnt_t / ngram_cnt_t.sum()

    return vocab, vocab_dic, vocab_dic_r, ngram_cnt, ngram_p, ngram_p_ao

###Read training & test files
# english train
eng_np_nd = preprocess("LangId.train.English")
# italian train
it_np_nd = preprocess("LangId.train.Italian")
# french train
fr_np_nd = preprocess("LangId.train.French")
# test
test_np_nd = preprocess("LangId.test")

""""**Design Choice 1**: 

Convert pure numbers to a representative dummy charater "N".

This is because the sequence of the numbers really do not mean anything different in any culture. Thus the different numbers in the train documents for different languages should not bias the algorithm to make inferences based on how similar the numbers are to the train texts.

**Design Choice 2**:

Keep record of the last letter in words. This includes single letter words. 
"""

### process lines into letter bigrams
# read english train doc to bigram letters
eng_nletters, eng_letter = ngrams_letters(eng_np_nd)

# get bigram probability
eng_l, eng_l_dic, eng_l_dic_r, eng_nl_cnt, eng_nl_p, eng_nl_p_ao= nletters_process(
    eng_nletters, eng_letter)

# read french train doc to bigram letters
fr_nletters, fr_letter = ngrams_letters(fr_np_nd)

# get bigram probability
fr_l, fr_l_dic, fr_l_dic_r, fr_nl_cnt, fr_nl_p, fr_nl_p_ao = nletters_process(
    fr_nletters, fr_letter)

# read italian train doc to bigram letters
it_nletters, it_letter = ngrams_letters(it_np_nd)

# get bigram probability
it_l, it_l_dic, it_l_dic_r, it_nl_cnt, it_nl_p, it_nl_p_ao = nletters_process(
    it_nletters, it_letter)

# save processed probabilities in a dictionary for easy access
l_dicts = dict(zip(["english","french","italian"],
                 [[eng_l_dic, eng_nl_p, eng_nl_p_ao],
                  [fr_l_dic, eng_nl_p, fr_nl_p_ao],
                  [it_l_dic, eng_nl_p, it_nl_p_ao]]))

#### Letter Bi-gram Test

l_lines, letters_test = l_keepLines(test_np_nd, n=2)

l_dicts = dict(zip(["english", "french", "italian"],
                   [[eng_l_dic, eng_nl_p, eng_nl_p_ao],
                    [fr_l_dic, fr_nl_p, fr_nl_p_ao],
                    [it_l_dic, it_nl_p, it_nl_p_ao]]))
"""
** Design Choice 3 **:

Calculate probabilities in exponential space to reduce computing complexity.

Since log(P1xP2xP3) = log(P1) + log(P2) + log(P3)
"""

def letter_likeliness(ngram, lg="english", smoothing=None):
    """calculate each bi-gram letters probability"""
    lead = ngram[0]
    follow = ngram[1]
    vocab_dic = l_dicts[lg][0]
    # nothing or add-one only (good-turing not included for letter bigrams)
    if smoothing == None:
        ngram_p = l_dicts[lg][1]
    if smoothing == "add-one":
        ngram_p = l_dicts[lg][2]
    # check p
    if lead in vocab_dic.keys():
        if follow in vocab_dic.keys():
            p_sub = ngram_p[vocab_dic[lead], vocab_dic[follow]]
        else:
            p_sub = 1e-10
    else:
        p_sub = 1e-10
    return np.log(p_sub)


def l_whatLg(test_dict, smoothing=None):
    p_lines = {}
    for k, v in test_dict.items():
        # english
        eng_prob = 1e-10
        for ngram in v:
            eng_prob += letter_likeliness(ngram, "english", smoothing)

        # french
        fr_prob = 1e-10
        for ngram in v:
            fr_prob += letter_likeliness(ngram, "french", smoothing)

        # italian
        it_prob = 1e-10
        for ngram in v:
            it_prob += letter_likeliness(ngram, "italian", smoothing)

        # find max probability
        players = {'English': eng_prob, 'French': fr_prob, 'Italian': it_prob}
        winner = max(players, key=players.get)
        p_lines[k] = winner

    return p_lines

l_out = l_whatLg(l_lines, "add-one")

# write out solution
with open("letterLangId.out", "w") as f:
    for k, v in l_out.items():
        f.writelines(" ".join([str(k+1), v, "\n"]))
    f.close()