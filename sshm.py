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

#TODO add comments to explain how the script works
#TODO add netbox integration
#TODO add ssh session logging

def create_hosts_dict(hosts_file):
    hosts = []
    try:
        with open(hosts_file, "r") as f:
            hosts = list(yaml.load_all(f, Loader=SafeLoader))
            hosts.sort(key=lambda k: (k['type'], k['hostname']))
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


@click.command(help = "Used to add a new host to sshm")
@click.option("--hostname", "-h", required=True, help = "descriptive name of host")
@click.option("--ip_address", "-ip", required=True, help = "ip address used to connect to host")
@click.option("--type", "-t", required=True, help="A generic type used to help organise hosts")
def add(hostname, ip_address, type):
    try:
        IPv4Address(ip_address)
    except AddressValueError:
        click.echo("Invalid IPv4 Address")
        sys.exit()
    table = Table(title="Added")
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    table.add_column("Type", justify="right", style="blue")
    hosts = create_hosts_dict(SSMHOSTS)
    host = {"hostname": hostname, "IP": ip_address, "type" : type, "key": None}
    hosts.append(host)
    update_sshmhosts(hosts, SSMHOSTS)
    table.add_row(host["hostname"], host["IP"], host["type"])
    console = Console()
    console.print(table)
    click.echo("added")


@click.command(help="Used to delete a host from sshm. Requires argument \"key\" which can be found using the \"sshm show\" command")
@click.argument("key")
def delete(key):
    table = Table(title="Deleted")
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    hosts = create_hosts_dict(SSMHOSTS)
    host = [i for i in hosts if (i["key"] == int(key))][0]
    hosts = [i for i in hosts if not (i["key"] == int(key))]
    update_sshmhosts(hosts, SSMHOSTS)
    table.add_row(host["hostname"], host["IP"])
    console = Console()
    console.print(table)


@click.command()
@click.option("--hostname", "-h", help = "Used to filter result by hostname. Can be full or just a part of hostname")
@click.option("--type", "-t", help = "Used to filter result by type. Can be full or just a part of type")
def show(hostname:str, type:str):
    table = Table(title="hosts")
    table.add_column("Key", justify="right", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    table.add_column("Type", justify="right", style="blue")
    hosts = create_hosts_dict(SSMHOSTS)
    if hostname:
        hosts = [i for i in hosts if hostname in i['hostname']]
    if type:
        hosts = [i for i in hosts if type in i['type']]
    for host in hosts:
        table.add_row(str(host["key"]), host["hostname"], host["IP"], host["type"])
    console = Console()
    console.print(table)


@click.command(help="shows all types used in existing hosts list")
def types():
    hosts = create_hosts_dict(SSMHOSTS)
    types = set([i["type"] for i in hosts])
    table = Table()
    table.add_column("Types", justify="left", style="cyan", no_wrap=True)
    for type in types:
        table.add_row(type)
    console = Console()
    console.print(table)



@click.command(help="Used to connect to host using the systems \"ssh\" command. Requires argument \"key\" which can be found using the \"sshm show\" command")
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
cli.add_command(types)

if __name__ == "__main__":
    cli()
