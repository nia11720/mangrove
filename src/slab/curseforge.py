import os

import click

from core import Httpx

version_to_id = lambda version: {
    "1.20.2": 10236,
    "1.20.4": 10407,
    "1.20.5": 10549,
}[version]


mods = [
    # masa
    ("malilib", 303119),
    ("minihud", 244260),
    ("tweakroo", 297344),
    ("litematica", 308892),
    ("item-scroller", 242064),
    # jade
    ("jade", 324717),
    # map
    ("xaero-minimap", 263420),
    ("xaero-worldmap", 317780),
    # carpet
    ("carpet", 349239),
    ("carpet-tis-addition", 397510),
    # world-edit
    ("worldedit", 225608),
    ("worldedit-cui", 402098),
]


@click.command
@click.option("--version", "-v", default="1.20.4")
def main(version):
    vid = version_to_id(version)

    httpx = Httpx(base_url="https://www.curseforge.com")
    for name, mid in mods:
        url = f"/api/v1/mods/{mid}/files"
        parmas = (
            "pageIndex=0&pageSize=20&sort=dateCreated&sortDescending=true&removeAlphas=true&"
            f"gameVersionId={vid}&gameFlavorId=4"
        )
        res = httpx.get(url, params=parmas)
        try:
            fid = res.json()["data"][0]["id"]
        except IndexError:
            print(f"faild: {name}")
            continue

        res = httpx.get(f"/api/v1/mods/{mid}/files/{fid}/download")
        dirname = os.path.expanduser("~/Downloads")
        with open(f"{dirname}/{name}-{version}-{fid}.jar", "wb") as fp:
            fp.write(res.content)


if __name__ == "__main__":
    main()
