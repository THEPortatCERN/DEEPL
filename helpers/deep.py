"""
Helper functions [ DEEP specific ]
"""
import pandas as pd
import json
import re
from classifier.NaiveBayesSKlearn import SKNaiveBayesClassifier

import googletrans
import langdetect


def get_processed_data(csv_file_path, delim=','):
    """
    return processed_data [(text, label), ... ] from csv file
    NOTE: the processed data should be csv with fields excerpt and sector
    """
    df = pd.read_csv(csv_file_path, sep=delim, error_bad_lines=False)
    punc_nums_preprocessor = SKNaiveBayesClassifier.preprocess
    processed = df.assign(excerpt=df['excerpt'].apply(punc_nums_preprocessor))
    excerpts = processed['excerpt']
    sector_labels = processed['sector']
    return list(zip(excerpts, sector_labels))


def create_processed_data(
        data,
        input_csv_path='_playground/sample_data/nlp_out_new.csv',
        output_csv_path='_playground/sample_data/processed_new_data.csv'):
    data = process_deep_entries_data(input_csv_path)
    excerpts, sectors = zip(*data)
    df_data = {'excerpt': excerpts, 'sector': sectors}
    df = pd.DataFrame(data=df_data)
    df.to_csv(output_csv_path)


def get_all_sectors(df):
    """
    Return raw list of sectors
    @df : DataFrame
    """
    lst = []
    for v in df[df['twodim'].notnull()][['twodim']].iterrows():
        for k in v[1].twodim:
            lst.append(k['sector'])
    return lst


def get_sector_excerpt(df, translate=False):
    """Return list of tuples with sector and excerpt -> [(excerpt, sector)...]
    @df : DataFrame
    """
    if translate:
        translator = googletrans.Translator()
    lst = []
    for v in df[df['twodim'].notnull()][['twodim', 'excerpt']].iterrows():
        for k in v[1].twodim:
            excerpt = v[1].excerpt
            if type(excerpt) != str or not excerpt.strip():
                continue
            excerpt = re.sub('[\r\n\t]', ' ', v[1].excerpt)
            if translate:
                try:
                    lang = langdetect.detect(excerpt)
                except Exception:
                    print(excerpt)
                    continue
                if lang != 'en':
                    excerpt = translator.translate(excerpt).text
            lst.append((excerpt, k['sector']))
    return lst


def get_sub_sectors_excerpt(df):
    """
    Return list of tuples with sector, subsectors and excerpt
    @df : DataFrame
    """
    lst = []
    for v in df[df['twodim'].notnull()][['twodim', 'excerpt']].iterrows():
        for k in v[1].twodim:
            lst.append(([k['sector'], k['subsectors']], v[1].excerpt))
    return lst


def process_deep_entries_data(csv_file_path):
    """
    Take in a csv file consisting of folloing columns:
        'onedim_j', 'twodim_j', 'reliability', 'severity', 'demo_groups_j',
        'specific_needs_j', 'aff_groups_j', 'geo_j', 'info_date', 'excerpt',
        'has_image', 'lead_text', 'lead_id', 'lead_url', 'event'
    Process it(remove stop words, translate language,...)
    And return list of tuples: [(text, label)...]
    """

    df = pd.read_csv(csv_file_path, header=0)
    # Convert json string columns to json
    df[df.filter(like="_j").columns] = df.filter(like="_j").applymap(
        lambda x: json.loads(x)
    )
    # Change column names
    for v in df.filter(like="_j"):
        df = df.rename(columns={v: '_'.join(v.split('_')[:-1])})

    # filter texts only if langid english

    return get_sector_excerpt(df)


# NOT USED
def get_deep_data(debug=True, filter_non_english=False, filepath=None):
    def printd(*args):
        if debug:
            print(*args)

    csv_file_path = '_playground/sample_data/nlp_out.csv'
    if filepath:
        csv_file_path = filepath

    printd('PROCESSING DEEP ENTRIES DATA')
    data = process_deep_entries_data(csv_file_path)
    if filter_non_english:
        data = [
            (str(ex), l) for (ex, l) in data if langid.classify(str(ex))[0] == 'en'
        ]
    printd('DONE')
    return data


# NOT USED, use scripts.create_classifier.create_classifier instead
def get_classifier(num=1000, confusion_mat=True, get_model=True, debug=True, data=None):
    """ TEMPORARY FUNCTION TO HELP WITH CREATING DEEP DATA"""
    def printd(*args):
        if debug:
            print(*args)

    from classifier.feature_selectors import UnigramFeatureSelector, BigramFeatureSelector
    from classifier.NaiveBayes_classifier import NaiveBayesClassifier
    from nltk.stem.porter import PorterStemmer
    import random
    import langid
    from helpers.common import (
        rm_punc_not_nums, rm_punc_not_nums_list,
        rm_stop_words_txt, rm_stop_words_txt_list,
        translate_to_english_txt,
        compose
    )

    printd('PROCESSING DEEP ENTRIES DATA')
    data = data or get_deep_data(debug)[:num]
    printd('DONE')

    printd('REMOVING PUNC AND STOP WORDS')
    stemmer = PorterStemmer()
    rm_punc_and_stop = compose(
        rm_punc_not_nums_list,
        rm_stop_words_txt_list,
        lambda x: list(map(str.lower, x)),
        lambda x: list(map(stemmer.stem,x)) # comment this if we don't need stemming
    )
    rm_punc_and_stop = lambda x: x
    data = [(rm_punc_and_stop(str(ex).split()), l) for (ex, l) in data if langid.classify(str(ex))[0] == 'en']
    printd('DONE')

    #data = [(list(movie_reviews.words(fileid)), category)
    #       for category in movie_reviews.categories()
    #      for fileid in movie_reviews.fileids(category)
    #]
    #printd(data[0])
    tags_data = {}
    for ex, l in data:
        tags_data[l] = tags_data.get(l, '') + " "+ str(ex)
        
    all_tokenized_documents = list(map(lambda x:x.split(), [v for k, v in tags_data.items()]))

    printd('SHUFFLING DATA')
    random.shuffle(data)
    printd('DONE')

    data_len = len(data)
    test_len = int(data_len * 0.25)

    printd('TAKING OUT TEST/TRAIN DATA')
    train_data = data[test_len:]
    printd("length of training data", len(train_data))
    test_data = data[:test_len]
    printd('DONE')

    printd('COUNTING TAG FREQUENCIES in TRAIN DATA')
    d = {}
    for ex, l in train_data:
        d[l] = d.get(l, 0) + 1
    printd(d)
    printd('DONE')

    printd('CREATING FEATURE SELECTOR')
    from classifier.tf_idf import relevant_terms
    #most_relevant_terms = list(relevant_terms(all_tokenized_documents))
    #selector = UnigramFeatureSelector.new(freq_words=most_relevant_terms)
    selector = UnigramFeatureSelector.new(corpus=data, top=2000) # use top 2000 words
    printd('DONE')

    # printd('CREATING BIGRAM FEATURE SELECTOR')
    # selector = BigramFeatureSelector.new(corpus=data, top=2000)
    # selector = DocumentFeatureSelector.new(corpus=data, top=2000)
    # printd('DONE')

    printd('CREATING CLASSIFIER')
    classifier = NaiveBayesClassifier.new(selector, train_data)
    printd('DONE')
    if not get_model:
        # test_data is returned for calculating accuracy outside this function
        return classifier, test_data

    printd('CALCULATING ACCURACY')
    printd(classifier.get_accuracy(test_data))

    if confusion_mat:
        printd('CONFUSION MATRIX')
        printd(classifier.get_confusion_matrix(test_data))

    import pickle
    from classifier.models import ClassifierModel
    c = ClassifierModel(
        name='Naive Bayes',
        version='1.1',
        data=pickle.dumps(classifier)
    )
    return c
