astrotrend
==========

it creates a chord diagram (and a simple word cloud too) to visualize word rate and co-occurrence in the titles of the arxiv.org preprints posted in the past 7 days. it requires a few packages, including urllib2, PIL and BeautifulSoup (for the latter a local copy of BeautifulSoup.py would do), and some d3 libraries (included)

no installation is required: just grab the python codes. the font used for the word cloud is provided for convenience, but of course it can be changed by feeding the appropriate path to the got in getwords.py

to run just type python getwords.py (tuple.py for the chord diagram)

as always, it is work in progress

it saves a png image of the cloud and an html file for the diagram. it may take a minute to create them.

[!alt text] ("http://cosmo.nyu.edu/~fb55/vizs/videos/2014-10-31_cooccurrence.png")
