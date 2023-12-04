import requests
import time
from bs4 import BeautifulSoup
import json
import os

resume_book_id = "svindkal/1947"
resume_page = 141

# Create necessary directories if they don't exist
if not os.path.exists("data/raw/svindkal"):
    os.makedirs("data/raw/svindkal")
if not os.path.exists("data/images/svindkal"):
    os.makedirs("data/images/svindkal")

def extract_book_text(page_source):
    start_tag = "<!-- mode=normal -->"
    end_tag = "<!-- NEWIMAGE2 -->"

    start_index = page_source.find(start_tag)
    end_index = page_source.find(end_tag)

    if start_index == -1 or end_index == -1:
        return None

    start_index += len(start_tag)
    book_text = page_source[start_index:end_index].strip()

    return book_text

def download_tiff_image(image_url, save_path, book_id, page_number):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(os.path.join(save_path, f"{book_id}_page_{page_number}.tif"), 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"TIFF image saved for page {page_number}")
    else:
        print(f"Failed to download TIFF image for page {page_number}. Status code: {response.status_code}")

def fetch_book_text_and_image(book_id, num_pages, start_page=1, end_page=793):
    for i in range(start_page, min(num_pages + 1, end_page + 1)):
        page_url = f"http://runeberg.org/{book_id}/{str(i).zfill(4)}.html"
        response = requests.get(page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract the text using the extract_book_text function
            book_text = extract_book_text(str(soup))

            if book_text:
                with open(f"data/raw/{book_id}_page_text_{i}.txt", "w", encoding="UTF-8") as f:
                    f.write(book_text)
                print(f"Text has been saved to {book_id}_page_text_{i}.txt", flush=True)
            else:
                print(f"Book text not found for page {i}.")

            # Find and download TIFF image
            tiff_link = soup.find('a', text="Full resolution (TIFF)")
            if tiff_link:
                image_url = "http://runeberg.org" + tiff_link['href']
                download_tiff_image(image_url, "data/images", book_id, i)

            # Wait for a respectful amount of time before making the next request
            time.sleep(5)
        else:
            print(f"Failed to fetch page {i}. Status code: {response.status_code}")

# Load the number of pages per book from JSON file
with open("data/number_of_pages_per_book.json", "r") as infile:
    number_of_pages_per_book = json.load(infile)

# Update the loop to resume from a specific book and page
found_resume_book = False
for book_id, num_pages in number_of_pages_per_book.items():
    if not found_resume_book:
        if book_id == resume_book_id:
            found_resume_book = True
            print(f"Resuming text and image fetching for {book_id}...")
            fetch_book_text_and_image(book_id, num_pages, resume_page, resume_page + 793)
        else:
            print(f"Skipping {book_id}...")
            continue
    else:
        print(f"Fetching text and image for {book_id}...")
        fetch_book_text_and_image(book_id, num_pages)
