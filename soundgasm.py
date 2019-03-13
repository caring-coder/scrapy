import os
import re
import shutil

from bs4 import BeautifulSoup
from tqdm import tqdm


session = None


def is_soundgasm_user_page_url(url: str):
    return re.match("^http(?:s)?://soundgasm\\.net/u/([^/]+)$", url)


def is_soundgasm_audio_page_url(url: str):
    return re.match("^http(?:s)?://soundgasm\\.net/u/([^/]+)/([^/]+)$", url)


def contains_soundgasm_audio_file_url(url: str):
    match = re.search("(https://soundgasm\\.net/sounds/.+\\.m4a)", url)
    return match


def extract_soundgasm_audio_file_url(url: str):
    search = re.search("(https://soundgasm\\.net/sounds/.+\\.m4a)", url)
    group = search.group(1)
    return group


def extract_user_from_soundgasm_audio_page_url(url: str):
    return re.search("^http(?:s)?://soundgasm\\.net/u/([^/]+)/([^/]+)$", url).group(1)


def extract_filename_from_soundgasm_audio_page_url(url: str):
    return re.search("^http(?:s)?://soundgasm\\.net/u/([^/]+)/([^/]+)$", url).group(2)


def extract_audio_file_url_from_soundgasm_audio_page_url(audio_page_url):
    with session.get(audio_page_url) as request:
        if request.status_code != 200:
            return None
        link_content = BeautifulSoup(request.content, "html.parser")
        for script in link_content.find_all('script'):
            if script.string:
                if contains_soundgasm_audio_file_url(script.string):
                    return extract_soundgasm_audio_file_url(script.string)
    return None


def extract_audio_from_url(audio_url, current_user, target_filename):
    os.makedirs("~/Téléchargements/Soundgasm/{}".format(current_user), exist_ok=True)
    filename = target_filename.replace("/", "-")
    if len(filename) > 240:
        filename = filename[0:240] + "..."
    filename = "~/Téléchargements/Soundgasm/{}/{}.m4a".format(current_user, filename)
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        with session.get(audio_url, stream=True) as request:
            with open(filename + ".wip", 'wb') as f:
                shutil.copyfileobj(request.raw, f)
        os.rename(filename + ".wip", filename)
    else:
        pass


users = [
    # "Qarnivore",
    # "Desdesbabypie",
    # "garden_slumber",
    # "Mangosonabeach",
    # "sassmastah77",
    # "rubber_foal",
    # "fieldsoflupine",
    # "sexuallyspecific",
    # "SarasSerenityndSleep",
    # "Lavendearie",
    # "miss_honey_bun",
    # "John17999"
]


def extract_audio_from_page_url(audio_page_url):
    with open("~/Téléchargements/Soundgasm/cache", "a+") as cache:
        if audio_page_url in cache.readlines():
            return
    if not is_soundgasm_audio_page_url(audio_page_url):
        raise Exception("{}".format("url not treated: {}".format(audio_page_url)).ljust(120, ' ')[0:120])
    user = extract_user_from_soundgasm_audio_page_url(audio_page_url)
    filename = extract_filename_from_soundgasm_audio_page_url(audio_page_url)
    audio_file_url = extract_audio_file_url_from_soundgasm_audio_page_url(audio_page_url)
    if audio_file_url:
        extract_audio_from_url(audio_file_url, user, filename)
        with open("~/Téléchargements/Soundgasm/cache", "a+") as cache:
            cache.write(audio_page_url + "\n")


def extract_all_public_audio_from_soundgasm_user(user_page_url: str):
    with session.get(user_page_url) as request:
        soup = BeautifulSoup(request.content, "html.parser")
    user_page_all_links = soup.find_all('a')
    for user_page_current_link in tqdm(user_page_all_links, desc="files"):
        user_page_current_link_value = user_page_current_link.get("href")
        if is_soundgasm_audio_page_url(user_page_current_link_value):
            extract_audio_from_page_url(user_page_current_link_value)


for user in users:
    extract_all_public_audio_from_soundgasm_user(user)


