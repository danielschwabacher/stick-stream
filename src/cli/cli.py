import click
from ..broadcaster import broadcast
from ..receiver import receive


@click.group()
@click.version_option(package_name="stick-stream")
def cli():
    """Stick-Stream — stream game controller input over the network."""
    pass


cli.add_command(broadcast)
cli.add_command(receive)
