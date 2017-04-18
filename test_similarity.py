
import kruncher.utils as utils
import elastic.similarity_greg as similarity

if __name__ == "__main__":
    # Load Services Settings
    settings = utils.loadxml("settings.xml")

    # Load JSON feed
    feed_json_file=settings.find('settings').find('feed_json_file').text
    json_data = utils.loadjson(feed_json_file)

    #debug
    #utils.printjsonTitles(json_data)

    # create dictionnary:
    token_dict = []

    # fill & compare
    token_dict.append("this is the new iphone red")
    print(similarity.find_similar(token_dict))
    token_dict.append("the iphone as a new color red")
    print(similarity.find_similar(token_dict))
    token_dict.append("samsung galaxy compete with iphone")
    print(similarity.find_similar(token_dict))
    token_dict.append("samsung is the first smartphone provider")
    print(similarity.find_similar(token_dict))
    token_dict.append("red iphone is available")
    print(similarity.find_similar(token_dict))
    token_dict.append("l'iphone rouge est disponible")
    print(similarity.find_similar(token_dict))
    token_dict.append("l'iphone rouge est là")
    print(similarity.find_similar(token_dict))
    token_dict.append("the biggest smartphone provider is samsung")
    print(similarity.find_similar(token_dict))

    # i=0
    # for token in token_dict :
    #     #print("  {} : {}".format(token, token_dict[token]))
    #     print("  {} : {}".format(i,token))
    #     i=i+1
    #
    # sim = similarity.find_similar(token_dict,3)
    # print(sim)


    # i=0
    # for news in json_data :
    #     for t in json_data[news] :
    #         if i < 5 :
    #             print("Adding news "+t['title'])
    #             token_dict.append(t['title'])
    #
    #             #for token in token_dict :
    #             #    print("  {} : {}".format(token, token_dict[token]))
    #
    #             sim = similarity.find_similar(token_dict,3)
    #             print(sim)
    #             i = i+1

    # similarity.add_news_to_dict(token_dict,"objets connectés n’étaient pas tout")
    # sim = similarity.find_similar(token_dict,3)
    # print(sim)
