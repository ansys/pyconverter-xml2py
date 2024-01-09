# Copyright (c) 2024 ANSYS, Inc. All rights reserved.

import os

from github import ContentFile, Github, Repository
import requests


def download(c: ContentFile, out: str):
    """
    This function initially comes from the following GitHub repository:
    https://github.com/Nordgaren/Github-Folder-Downloader

    """
    r = requests.get(c.download_url)
    output_path = f"{out}/{c.path}"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        print(f"downloading {c.path} to {out}")
        f.write(r.content)


def download_folder(repo: Repository, folder: str, out: str, recursive: bool):
    """
    This function initially comes from the following GitHub repository:
    https://github.com/Nordgaren/Github-Folder-Downloader

    """
    contents = repo.get_contents(folder)
    for c in contents:
        if c.download_url is None:
            if recursive:
                download_folder(repo, c.path, out, recursive)
            continue
        download(c, out)


def download_template():
    """Download the templage package provided by default."""

    g = Github()
    repo = g.get_repo("ansys/pyconverter-xml2py")
    download_folder(repo, "_package", ".", True)
