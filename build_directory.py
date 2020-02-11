from pathlib import Path

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

import feedparser
import subprocess
import typer

app = typer.Typer()

def get_episodes(rss_feed: str):
    p = feedparser.parse(rss_feed)
    return [episode for episode in p['items']]

@app.command()
def make_dirs(rss_feed: str):
    """For each episode in the RSS Feed, make a new directory"""
    title_list = [episode.title for episode in get_episodes(rss_feed)]

    for index, title in enumerate(title_list[::-1]):
        directory_name = f'{index + 1} - {title}'
        Path(directory_name).mkdir(exist_ok=True)
        typer.echo(f'{directory_name} created')

    return typer.echo('Done! ^_^!')


@app.command()
def add_summaries(rss_feed: str, template_filename: str=None):
    """For each episode get the summary and add it as `Summary.txt`.
To load a template, ensure there is a file with the given name.
    """
    episodes = get_episodes(rss_feed)

    if template_filename:
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(name=template_filename)

    for index, episode in enumerate(episodes[::-1]):
        directory = Path(f'{index + 1} - {episode.title}')

        if not directory.is_dir():
            make_dirs(rss_feed)

        with open(directory.joinpath('summary.txt'), 'w') as filename:
            summary = BeautifulSoup(episode.summary).get_text()

            if template_filename:
                summary = template.render(summary=summary, url=episode.link)

            filename.write(summary)

        typer.echo(f'Summary for {episode.title} added!')

    return typer.echo('Done! ^_^!')


@app.command()
def make_still_video(
        directory: str='',
        image: str='',
        audio: str='',
        speed='medium',
        output='output.mp4',
        ):
    """Create Video from Given Audio, Video"""

    if directory:
        image = list(
                filter(
                    lambda x: x.suffix in ['.jpg', '.png'],
                    Path(directory).iterdir()))[0]

        typer.echo(f'{image=}')

        audio = list(
                filter(
                    lambda x: x.suffix in ['.mp3', '.wav'],
                    Path(directory).iterdir()))[0]

        typer.echo(f'{audio=}')

        output = image.with_suffix('.mp4')

    cmd = ['ffmpeg', '-loop', '1', '-i', Path(image), '-i', Path(audio), '-c:a', 'aac', '-c:v', 'libx264', '-preset', speed,
            '-strict', 'experimental', '-loglevel', 'error', '-b:a', '192k', '-shortest', output]

    subprocess.run(cmd)
    return typer.echo('Done! ^_^!')


@app.command()
def bulk_still_video(path:str='.'):
    """Run make_still_video for every folder in the path"""
    for folder in Path(path).iterdir():
        if folder.is_dir():
            make_still_video(
                    directory=folder,
                    output=folder.with_suffix('.mp4'),
                    )

if __name__ == "__main__":
    app()

