import requests
from bs4 import BeautifulSoup
import threading
from queue import Queue
from urllib.parse import urljoin

class Crawler(threading.Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.visited_urls = set()  # Using a set for faster lookup

    def run(self):
        while True:
            url = self.queue.get()
            if url is None:
                break  # Exit loop if the queue is empty
            self.crawl(url)
            self.queue.task_done()

    def crawl(self, url):
        try:
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    print("Crawled:", url)
                    print("Title:", soup.title.text)
                    for link in soup.find_all('a'):
                        href = link.get('href')
                        if href and href.startswith('http'):
                            self.queue.put(href)
                else:
                    print("Failed to crawl:", url)
            else:
                print("Visited:", url)
        except Exception as e:
            print("Error crawling:", url, "-", e)

def main():
    seed_url = "https://example.com"
    num_threads = 5
    queue = Queue()
    crawler_threads = []

    # Create and start crawler threads
    for _ in range(num_threads):
        crawler = Crawler(queue)
        crawler.start()
        crawler_threads.append(crawler)

    # Enqueue the seed URL
    queue.put(seed_url)

    # Wait for all threads to finish
    queue.join()

    # Stop crawler threads by adding None to the queue
    for _ in range(num_threads):
        queue.put(None)

    # Wait for all crawler threads to finish
    for crawler in crawler_threads:
        crawler.join()

if __name__ == "__main__":
    main()
