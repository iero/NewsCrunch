import elastic.oldsim as similarity


if __name__ == "__main__":
    token_dict = {}
    similarity.initiate_dict(token_dict)

    similarity.add_news_to_dict(token_dict,"this is the new iphone red")
    #similarity.find_similar(token_dict, similarity.NB_NEWS)
    similarity.add_news_to_dict(token_dict,"the iphone as a new color red")
    #similarity.find_similar(token_dict, similarity.NB_NEWS)
    similarity.add_news_to_dict(token_dict,"samsung galaxy compete with iphone")
    # similarity.find_similar(token_dict, similarity.NB_NEWS)
    similarity.add_news_to_dict(token_dict,"samsung is the first smartphone provider")
    # similarity.find_similar(token_dict, similarity.NB_NEWS)
    similarity.add_news_to_dict(token_dict,"red iphone is available")
    # similarity.find_similar(token_dict, similarity.NB_NEWS)
    similarity.add_news_to_dict(token_dict,"l'iphone rouge est disponible")
    print(similarity.find_similar(token_dict, similarity.NB_NEWS))
