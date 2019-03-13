import re
import praw
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3 import Retry

import soundgasm

reddit = praw.Reddit("bot")

top_submissions = reddit.subreddit('gonewildaudio').top(limit=None)

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

soundgasm.session = session

errors = []

for submission in tqdm(top_submissions, desc="posts", total=1000):
    if soundgasm.is_soundgasm_audio_page_url(submission.url):
        soundgasm.extract_audio_from_page_url(submission.url)
    elif soundgasm.is_soundgasm_user_page_url(submission.url):
        soundgasm.extract_all_public_audio_from_soundgasm_user(submission.url)
    else:
        try:
            submission_links = BeautifulSoup(submission.selftext_html, "html.parser")\
                .find_all('a')
            for link in tqdm(submission_links, desc="links"):
                audio_page_url = link.get('href')
                if soundgasm.is_soundgasm_audio_page_url(audio_page_url):
                    soundgasm.extract_audio_from_page_url(audio_page_url)
                elif soundgasm.is_soundgasm_user_page_url(audio_page_url):
                    soundgasm.extract_all_public_audio_from_soundgasm_user(audio_page_url)
                elif re.match("/u/[^/]+", audio_page_url):
                    continue
                elif re.match("/r/[^/]+", audio_page_url):
                    continue
                elif re.match("http(s)?://www.reddit.com/u/.+", audio_page_url):
                    continue
                elif re.match("http(s)?://www.reddit.com/user/.+", audio_page_url):
                    continue
                elif re.match("http(s)?://www.reddit.com/r/.+", audio_page_url):
                    continue
                elif re.match("http(s)?://www.reddit.com/r/.+/comments/.+", audio_page_url):
                    continue
                elif re.match("http(s)?://old.reddit.com/", audio_page_url):
                    continue
                elif re.match("http(s)?://redd.it/.+", audio_page_url):
                    continue
                elif re.match("http(s)?://.*imgur.com/.+", audio_page_url):
                    continue
                elif re.match("http(s)?://.*pastebin.com/.+", audio_page_url):
                    continue
                elif re.match("http://chirb.it/.+", audio_page_url):
                    continue
                else:
                    continue
        except TypeError:
            errors.append("Failure to parse this submission : " + str(submission.permalink) + " : " + str(submission.url) + " selftext(" + str(submission.selftext_html) + ")")

for error in errors:
    print(error)
