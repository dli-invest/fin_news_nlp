from nlp_articles.app.nlp import init_nlp
# test with -s 
# pytest /workspaces/fin_news_nlp/nlp_articles/app/tests/test_nlp_dec2021_fix.py -s
def test_parsing_article():
    nlp = init_nlp("core/data/exchanges.tsv","core/data/indicies.tsv")
    text = '''
    The worst-performing tech stocks this week suggest the U.S. is done with Covid lockdowns
DocuSign, Etsy, DoorDash and Zoom are among the biggest losers, while HP, Apple and Cisco saw gains.
    '''

    doc = nlp(text)
    print(doc)
    text_list = [ent.text for ent in doc.ents]
    label_list = [ent.label_ for ent in doc.ents]
    expected_label_list = ['COUNTRY', 'COMPANY', 'COMPANY', 'COMPANY', 'COMPANY', 'STOCK', 'COMPANY', 'COMPANY']
    expected_ent_list = ['U.S.', 'DocuSign', 'Etsy', 'DoorDash', 'Zoom', 'HP', 'Apple', 'Cisco']

    assert len(text_list) == len(label_list)
    assert  expected_label_list == label_list


    assert expected_ent_list == text_list