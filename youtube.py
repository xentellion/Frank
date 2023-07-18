from googleapiclient.discovery import build


async def get_videos(path:str, dev_key: str, playlist_id: str, max_results: int = 50): 
    data = []
    # Send request through Youtube API
    with build('youtube', 'v3', developerKey= dev_key, cache_discovery=False) as service:
        while(1):
            try: 
                request = service.playlistItems().list(
                    part = "snippet",
                    playlistId = playlist_id,
                    maxResults = max_results,
                    pageToken = data[-1]["nextPageToken"]
                )
                data.append(request.execute())
            except Exception as e:
                request = service.playlistItems().list(
                        part = "snippet",
                        playlistId = playlist_id,
                        maxResults = max_results
                    )
                data.append(request.execute())
                if type(e) is KeyError:
                    break
    # get video links from data
    result = []
    for block in data:
        for item in block["items"]:
            result.append(item["snippet"]["resourceId"]["videoId"])
    result = list(set(result))
    result.sort()
    # Replace or send
    with open(f"{path}yt.txt", "a+") as file:
        file.seek(0)
        lines = file.read().splitlines()
        if lines != result:
            delta = list(set(result) - set(lines))
            file.truncate(0)
            for i in result:
                file.write(f'{i}\n')
            return delta
        else:
            return None
            