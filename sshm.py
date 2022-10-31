#!/usr/bin/env python

import yaml
import click
from yaml.loader import SafeLoader
import os
from rich.console import Console
from rich.table import Table
from ipaddress import IPv4Address, AddressValueError
import sys

SSMHOSTS = ".sshmhosts.yaml"

def create_hosts_dict(hosts_file):
    hosts = []
    try:
        with open(hosts_file, "r") as f:
            hosts = list(yaml.load_all(f, Loader=SafeLoader))
            for key, host in enumerate(hosts):
                host["key"] = key
            return hosts
    except:
        return hosts


def update_sshmhosts(hosts, hosts_file):
    for host in hosts:
        del host["key"]
    with open(hosts_file, "w") as f:
        f.write(yaml.dump_all(hosts))


@click.group()
def cli():
    pass


@click.command()
@click.option('--hostname','-h', required=True)
@click.option('--ip_address','-ip', required=True)
def add(hostname, ip_address):
    try:
        IPv4Address(ip_address)
    except AddressValueError:
        click.echo('Invalid IPv4 Address')
        sys.exit()
    table = Table(title="Added")
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    hosts = create_hosts_dict(SSMHOSTS)
    host = {"hostname": hostname, "IP": ip_address, "key": None}
    hosts.append(host)
    update_sshmhosts(hosts, SSMHOSTS)
    table.add_row(host['hostname'],host['IP'])
    console = Console()
    console.print(table)
    click.echo("added")

@click.command()
@click.argument("key")
def delete(key):
    table = Table(title="Deleted")
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    hosts = create_hosts_dict(SSMHOSTS)
    host = [i for i in hosts if (i["key"] == int(key))][0]
    hosts = [i for i in hosts if not (i["key"] == int(key))]
    update_sshmhosts(hosts, SSMHOSTS)
    table.add_row(host['hostname'],host['IP'])
    console = Console()
    console.print(table)


@click.command()
def show():
    table = Table(title="hosts")
    table.add_column('Key', justify="right", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    hosts = create_hosts_dict(SSMHOSTS)
    for host in hosts:
        table.add_row(str(host["key"]), host["hostname"], host["IP"])
    console = Console()
    console.print(table)

@click.command()
@click.argument("key")
def connect(key):
    hosts = create_hosts_dict(SSMHOSTS)
    for host in hosts:
        if host["key"] == int(key):
            os.system(f"ssh {host['IP']}")


cli.add_command(add)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(connect)

if __name__ == "__main__":
    cli()
