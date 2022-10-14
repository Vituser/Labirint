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

    def get_dict(self):
        return {
            'name': self.name,
            'author': self.author,
            'price': self.price,
            'old_price': self.old_price,
            'discount': self.discount,
            'img_url': self.img_url,
            'ebook_only': self.ebook_only,
        }

    def __str__(self):
        return f"Название: {self.name} Автор: {self.author} Цена: {self.price} Скидка: {self.discount}"


def get_html(url):
    headers = {
        "user-agent": "Mozilla / 5.0(X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 103.0.0.0 Safari / 537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }

    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    return soup


def save_json(file_name, data):
    with open(file_name, "w", encoding="UTF-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def get_books(main_url):
    books = []
    soup = get_html(url=main_url)

    pages_count = int(soup.find("div", class_="pagination-numbers").find_all("a")[-1].text)
    for page in range(1, pages_count + 1):
        url_page = main_url + f"?page={page}"

        soup = get_html(url=url_page)
        for i in range(2):
            books_items = soup.find_all("div", class_="genres-carousel__container")[i].find_all("div", "genres-carousel__item")
            for book_item in books_items:
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
                books.append(book)
    return books


def get_file_name(genre, name):
    time = datetime.date.today().strftime("%Y-%m-%d")
    file_name = f"{name}-{genre}-{time}.json"
    return file_name


def main():
    genre = "2308"
    file_name = get_file_name(genre, "labirint")
    url = f"https://www.labirint.ru/genres/{genre}/"

    books = get_books(main_url=url)
    books_dict = [book.get_dict() for book in books]
    save_json(file_name=file_name, data=books_dict)


if __name__ == "__main__":
    main()
