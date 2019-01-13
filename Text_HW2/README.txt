Instructions on running program files:
0. Change working directory to where the files are.

1. Please ensure the following documents are in the same folder as the program files:
- LangId.train.English
- LangId.train.Italian
- LangId.train.French
- LangId.test

2. names of the program files
1) letterLangId.py
- letter bigram model with no or add-one smoothing options.
2) wordLangId.py
- word bigram model with no or add-one smoothing options.
3) wordLangId2.py
- word bigram model with good-turing smoothing options.
- WARNING: this program runs really slowly

3. Depending on which ngram model you want to run, run in the command line.
e.g. "python letterLangId.py"

Question 1:

Can the letter bigram model be implemented without any kind of smoothing? 
> Yes. 
> Moreover, since there are not a lot of letters, it is most likely that all letter combinations have appeared in the training data. As a result the matrix is not quite spare. Smoothing is not neccessary.

What do you decide to do and why did you do it that way? And, if you decide to do smoothing, what kind of smoothing do you need to use to avoid zero-counts in the data? Would add-one smoothing be appropriate or you need better algorithms? Why (not)?
> I've decided to go with smoothing, however, as there are still certain combinations of letters that do not have any probability.
> Moreover, in order to decrease computational complexity, the probabilities will be added up in log space. Log does not work with 0 probabilities, thus add-one smoothing will enable bi-grams with 0 probability to be factored into the calculation without throwing out errors.
> Add-one is sufficient, even though the exact value that is added on can be tested to achieve the best result. In my case, besides adding one, I also arbitrarily used a arbitrary small number (1e-10) to represent 0 probability to enable log calculations.

How many times was your program correct?
>295 times

**Design Choice 1**: 

Convert pure numbers to a representative dummy character "N".

This is because the sequence of the numbers really do not mean anything different in any culture. Thus the different numbers in the train documents for different languages should not bias the algorithm to make inferences based on how similar the numbers are to the train texts.

**Design Choice 2**:

Keep record of the last letter in words. This includes single letter words. 

** Design Choice 3 **:

Calculate probabilities in exponential space to reduce computing complexity.

Since log(P1xP2xP3) = log(P1) + log(P2) + log(P3)

Question 2:
Can the letter bigram model be implemented without any kind of smoothing? 
> Yes. 
> However, the matrix is quite spare. Smoothing is not helpful.

What do you decide to do and why did you do it that way? And, if you decide to do smoothing, what kind of smoothing do you need to use to avoid zero-counts in the data? Would add-one smoothing be appropriate or you need better algorithms? Why (not)?
> I've decided to go with smoothing.
> Moreover, in order to decrease computational complexity, the probabilities will be added up in log space. Log does not work with 0 probabilities, thus add-one smoothing will enable bi-grams with 0 probability to be factored into the calculation without throwing out errors.
> Add-one is sufficient, even though the exact value that is added on can be tested to achieve the best result. In my case, besides adding one, I also arbitrarily used a arbitrary small number (1e-100) to represent 0 probability to enable log calculations.

How many times was your program correct?
>299 times

**Design Choice 1**: 

Convert pure numbers to a representative dummy word "NUMBER".

This is because the actual numbers really do not mean anything different in any culture. Thus the different numbers in the train documents for different languages should not bias the algorithm to make inferences based on how similar the numbers are to the train texts.

**Design Choice 2**:

All words that are next to each other in a sentence are treated as bigrams, regardless of whether they are separated by any punctuations.

** Design Choice 3 **:

Calculate probabilities in exponential space to reduce computing complexity.

Since log(P1xP2xP3) = log(P1) + log(P2) + log(P3)

Question 3:
How many times was your program correct?
>224 times

Which of the language models at Question#1, Question#2, and Question#3 is the best? 
The best one is words bigram with add-one smoothing.
,Pro, Con
Letter bigrams with add-one smoothing, simple to implement and low computational power needed, accuracy can be low (almost 2% lower than word bigrams) and more storage is needed to store all letter bigrams (compared to word bigrams)
Words bigram with add-one smoothing, high accuracy (highest among the three) and easy to calculate, cannot deal with single word in a sentence (e.g. agenda in the train doc)
Words bigram with good-turing smoothing, distribution more smoothed out, slow in computation (since one more step of calculation number of occurrences of each frequency) and requires lots of computational power + storage

**Design Choice 1**: 

Convert pure numbers to a representative dummy word "NUMBER".

This is because the actual numbers really do not mean anything different in any culture. Thus the different numbers in the train documents for different languages should not bias the algorithm to make inferences based on how similar the numbers are to the train texts.

**Design Choice 2**:

All words that are next to each other in a sentence are treated as bigrams, regardless of whether they are separated by any punctuations.

** Design Choice 3 **:

Calculate probabilities in exponential space to reduce computing complexity.
Since log(P1xP2xP3) = log(P1) + log(P2) + log(P3)

** Design Choice 4 **:

Instead of find the number of bi-grams with a count of C+1, move up directly up to the next count observed in the training document. For the number of bi-grams with the max count, the count is kept at the max.



