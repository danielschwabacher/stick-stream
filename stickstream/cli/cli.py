import click
from stickstream.broadcaster.broadcaster import broadcast
from stickstream.receiver.receiver import receive


@click.group()
@click.version_option(package_name="stick-stream")
def cli():
    """stick-stream — stream game controller input over the network."""
    pass


cli.add_command(broadcast)
cli.add_command(receive)
