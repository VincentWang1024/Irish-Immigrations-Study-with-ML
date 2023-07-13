from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("apify_api_D3HiJbuiORLbff7qnZLUJJJaoG5WFh3PbVlD")

def crawl_YT_urls(topic):

    # Prepare the Actor input
    run_input = {
        "searchKeywords": topic,
        "maxResults": 10,
        "startUrls": [],
        "simplifiedInformation": False,
        "saveShorts": False,
        "maxResultsShorts": 10,
        "saveStreams": False,
        "maxResultStreams": 10,
        "maxComments": 0,
        "subtitlesLanguage": "en",
        "subtitlesFormat": "srt",
        "proxyConfiguration": { "useApifyProxy": True },
    }

    # Run the Actor and wait for it to finish
    run = client.actor("bernardo/youtube-scraper").call(run_input=run_input)

    # Fetch and print Actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        print(item['url'])


def crawl_TT_urls(topic):
    # Prepare the Actor input
    run_input = {
        "hashtags": topic,
        "resultsPerPage": 20,
        "scrapeEmptyChannelInfo": False,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "proxyConfiguration": { "useApifyProxy": True },
    }

    # Run the Actor and wait for it to finish
    run = client.actor("clockworks/free-tiktok-scraper").call(run_input=run_input)

    # Fetch and print Actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        print(item['webVideoUrl'])



crawl_YT_urls('immigrant ireland')
# crawl_TT_urls(['IrelandIsFull', 'irishfirst', 'irelandimigration'])

