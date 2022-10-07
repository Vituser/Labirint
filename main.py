import json
import datetime
import requests
from bs4 import BeautifulSoup


class Book:
    empty_img_url = "https://img.labirint.ru/design/emptycover-big.svg"

    def __init__(self, name='', author='', price=-1, old_price=-1, discount=0, img_url=empty_img_url, ebook_only=False):
        self.name = name
        self.author = author
        self.price = price
        self.old_price = old_price
        self.discount = discount
        self.img_url = img_url
        self.ebook_only = ebook_only
        self.time = datetime.date.today().strftime("%Y-%m-%d")

    def get_dict(self):
        return {
            'name': self.name,
            'author': self.author,
            'price': self.price,
            'old_price': self.old_price,
            'discount': self.discount,
            'img_url': self.img_url,
            'ebook_only': self.ebook_only,
            'time': self.time,
        }

    def __str__(self):
        return f"Название: {self.name} Автор: {self.author} Цена: {self.price} Скидка: {self.discount}"


BOOKS = []


def get_data():
    headers = {
        "user-agent": "Mozilla / 5.0(X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 103.0.0.0 Safari / 537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }
    genre_num = "2308"
    file_name = f"labirint-{genre_num}.json"
    main_url = f"https://www.labirint.ru/genres/{genre_num}/"

    response = requests.get(url=main_url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    pages_count = int(soup.find("div", class_="pagination-numbers").find_all("a")[-1].text)
    for page in range(1, pages_count + 1):
        url = main_url + f"?page={page}"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        for i in range(2):
            books_items = soup.find_all("div", class_="genres-carousel__container")[i].find_all("div", "genres-carousel__item")
            for i, book_item in enumerate(books_items):
                book = Book()
                try:
                    b_info = book_item.find_all("div", class_="product need-watch")[0].find("div", class_="product-cover")
                except IndexError:
                    b_info = book_item.find_all("div", class_="product need-watch product_ebooks")[0].find("div", class_="product-cover")
                    book.ebook_only = True

                b_title = b_info.find("a")["title"]
                b_title_idx = b_title.find(" - ")
                book.author = b_title[:b_title_idx]
                book.name = b_title[b_title_idx+3:]
                book.price = b_info.find("span", class_="price-val").find("span").text.replace(" ", "")
                try:
                    book.old_price = b_info.find("span", class_="price-gray").text.replace(" ", "")
                except AttributeError:
                    pass
                try:
                    book.discount = b_info.find("span", class_="price-val")['title'].split("% ")[0]
                except KeyError:
                    pass
                book.img_url = b_info.find("img")['data-src']
                BOOKS.append(book)

    books_dict = [book.get_dict() for book in BOOKS]
    print(len(BOOKS))
    with open(file_name, "w", encoding="UTF-8") as file:
        json.dump(books_dict, file, indent=4, ensure_ascii=False)


def main():
    get_data()


if __name__ == "__main__":
    main()
