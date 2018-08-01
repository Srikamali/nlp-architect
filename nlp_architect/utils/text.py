# ******************************************************************************
# Copyright 2017-2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
import sys
import re

import spacy
from spacy.cli.download import download as spacy_download
from nltk.stem.snowball import EnglishStemmer
from nltk import WordNetLemmatizer
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES

from nlp_architect.utils.generic import license_prompt


class Vocabulary:
    """
    A vocabulary that maps words to ints (storing a vocabulary)
    """

    def __init__(self, start=0):

        self._vocab = {}
        self._rev_vocab = {}
        self.next = start

    def add(self, word):
        """
        Add word to vocabulary

        Args:
            word (str): word to add

        Returns:
            int: id of added word
        """
        if word not in self._vocab.keys():
            self._vocab[word] = self.next
            self._rev_vocab[self.next] = word
            self.next += 1
        return self._vocab.get(word)

    def word_id(self, word):
        """
        Get the word_id of given word

        Args:
            word (str): word from vocabulary

        Returns:
            int: int id of word
        """
        return self._vocab.get(word, None)

    def __len__(self):
        return len(self._vocab)

    def id_to_word(self, wid):
        """
        Word-id to word (string)

        Args:
            wid (int): word id

        Returns:
            str: string of given word id
        """
        return self._rev_vocab.get(wid)

    @property
    def vocab(self):
        """
        dict: get the dict object of the vocabulary
        """
        return self._vocab

    def add_vocab_offset(self, offset):
        """
        Adds an offset to the ints of the vocabulary

        Args:
            offset (int): an int offset
        """
        new_vocab = {}
        for k, v in self.vocab.items():
            new_vocab[k] = v + offset
        self.next += offset
        self._vocab = new_vocab
        self._rev_vocab = {v: k for k, v in new_vocab.items()}

    def reverse_vocab(self):
        """
        Return the vocabulary as a reversed dict object

        Returns:
            dict: reversed vocabulary object
        """
        return self._rev_vocab


def is_spacy_model_installed(model_name):
    try:
        spacy.load(model_name)
        return True
    except OSError:
        return False


class SpacyInstance:
    """
    Spacy pipeline wrapper which prompts user for model download authorization.

    Args:
        model (str, optional): spacy model name (default: english small model)
        disable (list of string, optional): pipeline annotators to disable
            (default: [])
    """

    def __init__(self, model='en', disable=None):
        if disable is None:
            disable = []
        try:
            self._parser = spacy.load(model, disable=disable)
        except OSError:
            url = 'https://spacy.io/models'
            if license_prompt('Spacy {} model'.format(model), url) is False:
                sys.exit(0)
            spacy_download(model)
            self._parser = spacy.load(model, disable=disable)

    @property
    def parser(self):
        """return Spacy's instance parser"""
        return self._parser

    def tokenize(self, text):
        """
        Tokenize a sentence into tokens
        Args:
            text (str): text to tokenize

        Returns:
            list: a list of str tokens of input
        """
        # pylint: disable=not-callable

        return [t.text for t in self.parser(text)]


stemmer = EnglishStemmer()
lemmatizer = WordNetLemmatizer()
spacy_lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
p = re.compile(r'[ \-,;.@&_]')


def simple_normalizer(text):
    """
    Simple text normalizer. Runs each token of a phrase thru wordnet lemmatizer
    and a stemmer.
    """
    if not str(text).isupper() or \
            not str(text).endswith('S') or \
            not len(text.split()) == 1:
        tokens = list(filter(lambda x: len(x) != 0, p.split(text.strip())))
        text = ' '.join([stemmer.stem(lemmatizer.lemmatize(t))
                         for t in tokens])
    return text


def spacy_normalizer(text, lemma=None):
    """
    Simple text normalizer using spacy lemmatizer. Runs each token of a phrase
    thru a lemmatizer and a stemmer.
    Arguments:
        text(string): the text to normalize.
        lemma(string): lemma of the given text. in this case only stemmer will
        run.
    """
    if not str(text).isupper() or \
            not str(text).endswith('S') or \
            not len(text.split()) == 1:
        tokens = list(filter(lambda x: len(x) != 0, p.split(text.strip())))
        if lemma:
            lemma = lemma.split(' ')
            text = ' '.join([stemmer.stem(l)
                             for l in lemma])
        else:
            text = ' '.join([stemmer.stem(spacy_lemmatizer(t, u'NOUN')[0])
                             for t in tokens])
    return text
