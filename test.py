
import requests
print("hello monomon")
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "VlL3esMeQRAzGnVCtjeqQ", "isbns": "9781632168146"})
print(res.json())