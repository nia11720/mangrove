import os

from core import huey
from youtube import app
from youtube.extensions import httpx, redis

client = app.test_client()


@huey.task(retries=5, retry_delay=10, priority=-1)
def download_video(id, itag="18"):
    task_id = f"downloading:{id}-{itag}"
    if task := redis.hgetall(task_id):
        url, filename, offset = task["url"], task["filename"], int(task["offset"])
    else:
        data = client.get(f"/video/stream?id={id}").json
        title, url = f"{data['title']}[{id}-{itag}]", data["urls"][itag]
        filename = os.path.expanduser(f"~/storage/movies/{title}.mp4.partial")
        offset = 0

        mapping = {"url": url, "filename": filename, "offset": offset}
        redis.hset(task_id, mapping=mapping)

    range_start, range_end = offset, offset + 8_388_607
    res = httpx.get(url, headers={"Range": f"bytes={range_start}-{range_end}"})

    with open(filename, "ab") as fp:
        nbytes = fp.write(res.content)

    if res.status_code == 206:
        redis.hincrby(task_id, "offset", nbytes)
        download_video(id, itag, priority=0)
    else:
        redis.delete(task_id)
        os.rename(filename, filename[:-8])


@huey.task()
def download_playlist(id, itag="18"):
    playlist = client.get(f"/playlist/?id={id}").json
    for video in playlist["items"]:
        download_video(video["id"], itag)
