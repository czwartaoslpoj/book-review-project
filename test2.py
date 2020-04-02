import requests

def getIsbnReviewFromGoodReadsApi(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "VlL3esMeQRAzGnVCtjeqQ", "isbns": isbn})
    return res.json()

jsonResponse = getIsbnReviewFromGoodReadsApi("0553803700")
print(jsonResponse["books"][0]["average_rating"])
# obj -> key:value 
# value -> array [objects]
# objects -> key:value
# {
#     'books': [
#         {
#             'id': 210329, 
#             'isbn': '1416949658', 
#             'isbn13': '9781416949657', 
#             'ratings_count': 44528, 
#             'reviews_count': 65462, 
#             'text_reviews_count': 1719, 
#             'work_ratings_count': 49226, 
#             'work_reviews_count': 73626, 
#             'work_text_reviews_count': 2311, 
#             'average_rating': '4.07'
#         },
#     ]
# }