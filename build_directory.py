from pathlib import Path

from bs4 import BeautifulSoup
import feedparser
import typer
from jinja2 import Environment, FileSystemLoader

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



if __name__ == "__main__":
    app()

