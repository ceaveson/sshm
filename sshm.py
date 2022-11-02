#!/usr/bin/env python

import yaml
import click
from yaml.loader import SafeLoader
import os
from rich.console import Console
from rich.table import Table
from ipaddress import IPv4Address, AddressValueError
import sys
from appdirs import user_config_dir, user_data_dir
import tomli

DEFAULT_SSHMCONFIG = """
#############################################################################
#                            sshm config                                    #
#############################################################################
# config file for variables that can be modified by the user
# uncomment any variables you want to change


# Normally the system username is the login name used for SSH connections
# LOGIN_NAME allows you to change the default login name to something else 

#LOGIN_NAME = "username"


# sshm checks what OS it is being ran on and stores the sshmhosts file in
# a reasonable place for that OS. If you want this stored somewhere else 
# then SSHMHOSTS will overwrite where it is stored. 

#SSHMHOSTS = "~/sshmhosts.yaml"
"""

SSHMCONFIG = os.path.join(user_config_dir(), "sshmconfig.toml")

if not os.path.exists(SSHMCONFIG):
    with open(SSHMCONFIG, "w") as f:
        f.write(DEFAULT_SSHMCONFIG)

with open(SSHMCONFIG, "rb") as f:
    config_dict = tomli.load(f)
try:
    LOGIN_NAME = config_dict["LOGIN_NAME"]
except:
    LOGIN_NAME = None
try:
    SSHMHOSTS = config_dict["SSHMHOSTS"]
except:
    SSHMHOSTS = os.path.join(user_data_dir(), "sshmhosts.yaml")


# TODO add comments to explain how the script works
# TODO add netbox integration


def create_hosts_dict(hosts_file):
    hosts = []
    try:
        with open(hosts_file, "r") as f:
            hosts = list(yaml.load_all(f, Loader=SafeLoader))
            hosts.sort(key=lambda k: (k["type"], k["hostname"]))
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


@click.command(help="Used to add a new host to sshm")
@click.option("--hostname", "-h", required=True, help="descriptive name of host")
@click.option(
    "--ip_address", "-ip", required=True, help="ip address used to connect to host"
)
@click.option(
    "--type", "-t", required=True, help="A generic type used to help organise hosts"
)
def add(hostname, ip_address, type):
    try:
        IPv4Address(ip_address)
    except AddressValueError:
        click.echo("Invalid IPv4 Address")
        sys.exit()
    table = Table(title="Added")
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    table.add_column("Type", justify="right", style="cyan")
    hosts = create_hosts_dict(SSHMHOSTS)
    host = {"hostname": hostname, "IP": ip_address, "type": type, "key": None}
    hosts.append(host)
    update_sshmhosts(hosts, SSHMHOSTS)
    table.add_row(host["hostname"], host["IP"], host["type"])
    console = Console()
    console.print(table)
    click.echo("added")


@click.command(help="Used to delete a host from sshm")
@click.argument("key")
def delete(key):
    table = Table(title="Deleted")
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    hosts = create_hosts_dict(SSHMHOSTS)
    host = [i for i in hosts if (i["key"] == int(key))][0]
    hosts = [i for i in hosts if not (i["key"] == int(key))]
    update_sshmhosts(hosts, SSHMHOSTS)
    table.add_row(host["hostname"], host["IP"])
    console = Console()
    console.print(table)


@click.command(help="show all hosts, view can be filtered with various options")
@click.option(
    "--hostname",
    "-h",
    help="Used to filter result by hostname. Can be full or just a part of hostname",
)
@click.option(
    "--type",
    "-t",
    help="Used to filter result by type. Can be full or just a part of type",
)
def show(hostname: str, type: str):
    table = Table(title="hosts")
    table.add_column("Key", justify="right", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    table.add_column("Type", justify="right", style="cyan")
    hosts = create_hosts_dict(SSHMHOSTS)
    if hostname:
        hosts = [i for i in hosts if hostname.lower() in i["hostname"].lower()]
    if type:
        hosts = [i for i in hosts if type.lower() in i["type"].lower()]
    for host in hosts:
        table.add_row(str(host["key"]), host["hostname"], host["IP"], host["type"])
    console = Console()
    console.print(table)
    click.echo(SSHMHOSTS)
    click.echo(SSHMCONFIG)


@click.command(help="shows all types used in existing hosts list")
def types():
    hosts = create_hosts_dict(SSHMHOSTS)
    types = set([i["type"] for i in hosts])
    table = Table()
    table.add_column("Types", justify="left", style="cyan", no_wrap=True)
    for type in types:
        table.add_row(type)
    console = Console()
    console.print(table)


@click.command(help='Used to connect to host using the systems "ssh" command')
@click.option("-l", "--login_name")
@click.argument("key")
def connect(key, login_name):
    hosts = create_hosts_dict(SSHMHOSTS)
    for host in hosts:
        if host["key"] == int(key):
            if login_name:
                os.system(f"ssh {login_name}@{host['IP']}")
            elif LOGIN_NAME:
                os.system(f"ssh {LOGIN_NAME}@{host['IP']}")
            else:
                os.system(f"ssh {host['IP']}")


@click.command(help="Shows config variables. They can all be changed in SSHMCONFIG with the exception of SSHMCONFIG itself")
def config():
    table = Table()
    table.add_column("Key", justify="right", style="cyan", no_wrap=True)
    table.add_column("value", style="magenta")
    if LOGIN_NAME:
        table.add_row("LOGIN_NAME", LOGIN_NAME)
    else:
        table.add_row(
            "LOGIN_NAME", "No LOGIN_NAME in SSHMCONFIG, system username will be used."
        )
    table.add_row("SSHMHOSTS", SSHMHOSTS)
    table.add_row("SSHMCONFIG", SSHMCONFIG)
    console = Console()
    console.print(table)


cli.add_command(add)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(connect)
cli.add_command(types)
cli.add_command(config)

if __name__ == "__main__":
    cli()
