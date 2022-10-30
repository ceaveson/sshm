#!/usr/bin/env python

import yaml
import click
from yaml.loader import SafeLoader
import os
from rich.console import Console
from rich.table import Table


def create_hosts_dict():
    hosts = []
    try:
        with open(".sshmhosts.yaml", "r") as f:
            hosts = list(yaml.load_all(f, Loader=SafeLoader))
            for key, host in enumerate(hosts):
                host["key"] = key
            return hosts
    except:
        return hosts


def update_sshmhosts(hosts):
    for host in hosts:
        del host["key"]
    with open(".sshmhosts.yaml", "w") as f:
        f.write(yaml.dump_all(hosts))


@click.group()
def cli():
    pass


@click.command()
def add():
    hosts = create_hosts_dict()
    hostname = click.prompt("Hostname")
    IP = click.prompt("IP Address")
    click.echo(f"Hostname: {hostname}")
    click.echo(f"IP Address: {IP}")
    confirm = f"""Are these details correct?
    Hostname {hostname}
    IP Address {IP}
    """
    if click.confirm(confirm):
        host = {"hostname": hostname, "IP": IP, "key": None}
        hosts.append(host)
        update_sshmhosts(hosts)
        click.echo("added")
    else:
        click.echo("not added")


@click.command()
@click.argument("key")
def delete(key):
    hosts = create_hosts_dict()
    hosts = [i for i in hosts if not (i["key"] == int(key))]
    update_sshmhosts(hosts)
    click.echo(f"removed {key}")


@click.command()
def show():
    table = Table(title="hosts")
    table.add_column('Key', justify="right", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    hosts = create_hosts_dict()
    for host in hosts:
        table.add_row(str(host["key"]), host["hostname"], host["IP"])
    console = Console()
    console.print(table)

"""    for host in hosts:
        table.add_row(host['key'], host['hostname'], host['IP'])
"""

@click.command()
@click.argument("key")
def connect(key):
    hosts = create_hosts_dict()
    for host in hosts:
        if host["key"] == int(key):
            os.system(f"ssh {host['IP']}")


cli.add_command(add)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(connect)

if __name__ == "__main__":
    cli()
