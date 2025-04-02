#!/usr/bin/env python3
import httpx, json, datetime
from feedgen.feed import FeedGenerator
from bs4 import BeautifulSoup

# Get JSON from RocaNews
response = httpx.get("https://thecurrent.rocanews.com/?_data=routes/index")
content  = json.loads(response.text)

# Instantiate feed object, set feed info
fg: FeedGenerator = FeedGenerator()
fg.id(id=content["publication"]["id"])
fg.title(title=content["metaTitle"])
fg.description(description=content["metaDescription"])
fg.link(href=content["publication"]["url"], rel="alternate")
fg.image(url=content["publication"]["logo"]["url"], link=content["publication"]["url"], title=content["metaTitle"])
fg.language(language="en")

cp = "© " + str(datetime.datetime.now().year) + " " + content["publication"]["copyright_text"]
fg.copyright(copyright=cp)

# Get posts
for post in content["paginatedPosts"]["posts"]:
    # Generate link, we'll need this for the post link and to get content
    link = "https://thecurrent.rocanews.com/p/" + post["slug"]

    # Build the feed entry
    fe = fg.add_entry()
    fe.guid(guid=post["id"])
    fe.title(title=post["meta_default_title"])
    fe.description(description=post["meta_default_description"])
    fe.link(href=link)
    fe.published(published=post["created_at"])
    fe.updated(updated=post["updated_at"])

    # Fetch the content and populate the post
    response     = httpx.get(link)
    full_content = response.text
    soup         = BeautifulSoup(full_content, "html.parser")
    content      = soup.find(name="div", id="content-blocks")
    fe.content(content=str(content))

# Write atom/rss to files
bs = BeautifulSoup(fg.rss_str(), 'xml')
pretty_rss = bs.prettify()
with open("rss.xml", "w") as rss_file:
    rss_file.write(str(pretty_rss))

bs = BeautifulSoup(fg.atom_str(), 'xml')
pretty_atom = bs.prettify()
with open("atom.xml", "w") as atom_file:
    atom_file.write(str(pretty_atom))