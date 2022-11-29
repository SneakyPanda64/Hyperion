# from transformers import pipeline
# import os
#
# image_to_text = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
#
# image_texts = []
# for v in os.listdir("images"):
#     image_texts.append(image_to_text(os.path.join("images", v))[0]["generated_text"])
# print(image_texts)



# from sentence_transformers import SentenceTransformer, util
# import torch
# embedder = SentenceTransformer('all-MiniLM-L6-v2')
# corpus = ['a screen shot of a computer screen with a message on it', 'a person doing exercises', 'a person using a filer', 'a picture of a person trading stocks', 'a black and white photo of a keyboard ', 'a desk with a wooden cabinet and a black chair ', 'a brown dog with a brown face and a brown collar ', 'a large group of bananas hanging from a tree ']
# corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)
# queries = ["What is a data structure"]
# top_k = min(5, len(corpus))
# for query in queries:
#     query_embedding = embedder.encode(query, convert_to_tensor=True)
#     cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
#     top_results = torch.topk(cos_scores, k=top_k)
#     print("Query:", query)
#     for score, idx in zip(top_results[0], top_results[1]):
#         print(corpus[idx], "(Score: {:.4f})".format(score))
# import keyphrase
# model_name = "ml6team/keyphrase-generation-t5-small-inspec"
# generator = keyphrase.KeyphraseGenerationPipeline(model=model_name)
# keyphrases = generator("Strict evaluation means that a computer system will only count the number of times a certain comparison is made. Loose evaluation means that a computer system will count any number of comparisons as long as they meet certain conditions.")
# print(keyphrases)
text = "There are a number of benefits that can be gained from using system dynamics in business, one being that system dynamics can provide a better understanding of how different variables interact over time.\nThis understanding can be used to create better business models and strategies.\nAnother benefit is that system dynamics can help to identify and correct problems early on in a system's development.\nThis can lead to improved stability and performance within a system.\nLast but not least, system dynamics can help to improve the communication and coordination within a business.\nBy understanding how different groups within a business are interacting, system dynamics can help to create better outcomes.\nIn short, business dynamics is a set of tools that can be used to improve the performance of a business.\nIt allows for better decisions to be made by allowing people to understand how different variables affect each other\n\nBusiness dynamics is a set of tools that can be used to improve the performance of a business.\nIt allows for better decisions to be made by allowing people to understand how different variables affect each other"
print(len(text.split(" ")))
cap = 50
words = 0
sentence = ""
for v in text.split("\n"):
    if words < cap:
        words += len(v.split(" "))
        sentence += v + " "
        print(words)
print(sentence)