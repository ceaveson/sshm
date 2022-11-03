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
import pynetbox

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


# If you have Netbox then this script can sync the hosts from there which have a primary IP.

#NETBOX_URL = https://netbox.example.com
#NETBOX_TOKEN = an_example_token

# May be required if using self signed cert
#HTTP_SESSION_VERIFY = False
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
try:
    NETBOX_URL = config_dict["NETBOX_URL"]
except:
    NETBOX_URL = None
try:
    NETBOX_TOKEN = config_dict["NETBOX_TOKEN"]
except:
    NETBOX_TOKEN = None
try:
    HTTP_SESSION_VERIFY = config_dict["HTTP_SESSION_VERIFY"]
except:
    HTTP_SESSION_VERIFY = None


# TODO add comments to explain how the script works


def create_hosts_dict(hosts_file):
    hosts = []
    try:
        with open(hosts_file, "r") as f:
            hosts = list(yaml.load_all(f, Loader=SafeLoader))
            hosts.sort(key=lambda k: (k["manufacturer"], k["hostname"]))
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
    "--manufacturer",
    "-m",
    required=True,
    help="A generic manufacturer used to help organise hosts",
)
def add(hostname, ip_address, manufacturer):
    try:
        IPv4Address(ip_address)
    except AddressValueError:
        click.echo("Invalid IPv4 Address")
        sys.exit()
    table = Table(title="Added")
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    table.add_column("manufacturer", justify="right", style="cyan")
    hosts = create_hosts_dict(SSHMHOSTS)
    host = {
        "hostname": hostname,
        "IP": ip_address,
        "manufacturer": manufacturer,
        "key": None,
        "source": "local",
    }
    hosts.append(host)
    update_sshmhosts(hosts, SSHMHOSTS)
    table.add_row(host["hostname"], host["IP"], host["manufacturer"])
    console = Console()
    console.print(table)
    click.echo("added")


@click.command(help="Used to delete a host from sshm")
@click.argument("key")
def delete(key):
    try:
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
    except IndexError:
        click.echo("No hosts left to delete!")


@click.command(help="show all hosts, view can be filtered with various options")
@click.option(
    "--hostname",
    "-h",
    help="Used to filter result by hostname. Can be full or just a part of hostname",
)
@click.option(
    "--manufacturer",
    "-m",
    help="Used to filter result by manufacturer. Can be full or just a part of manufacturer",
)
@click.option(
    "--source",
    "-s",
    help="Used to filter result by source (either local or netbox)",
)
def show(hostname: str, manufacturer: str, source: str):
    table = Table(title="hosts")
    table.add_column("Key", justify="right", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="magenta")
    table.add_column("IP", justify="right", style="green")
    table.add_column("manufacturer", justify="right", style="cyan")
    table.add_column("source", justify="right", style="magenta")
    hosts = create_hosts_dict(SSHMHOSTS)
    if hostname:
        hosts = [i for i in hosts if hostname.lower() in i["hostname"].lower()]
    if manufacturer:
        hosts = [i for i in hosts if manufacturer.lower() in i["manufacturer"].lower()]
    if source:
        hosts = [i for i in hosts if source.lower() in i["source"].lower()]
    for host in hosts:
        table.add_row(
            str(host["key"]),
            host["hostname"],
            host["IP"],
            host["manufacturer"],
            host["source"],
        )
    console = Console()
    console.print(table)


@click.command(help="shows all manufacturers used in existing hosts list")
def manufacturers():
    hosts = create_hosts_dict(SSHMHOSTS)
    manufacturers = set([i["manufacturer"] for i in hosts])
    table = Table()
    table.add_column("manufacturers", justify="left", style="cyan", no_wrap=True)
    for manufacturer in manufacturers:
        table.add_row(manufacturer)
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


@click.command(
    help="Shows config variables. They can all be changed in SSHMCONFIG with the exception of SSHMCONFIG itself"
)
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


@click.command(
    help='If you have Netbox, use this to sync your hosts. Requires Netbox url and \
                     token adding to SSHMCONFIG file. Do "sshm config" to see where this file is located'
)
def sync():
    if NETBOX_URL and NETBOX_TOKEN:
        nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)
        if HTTP_SESSION_VERIFY == False:
            nb.http_session.verify = False
        devices = nb.dcim.devices.filter(has_primary_ip=True)
        hosts = create_hosts_dict(SSHMHOSTS)
        hosts = [i for i in hosts if not (i["source"] == "netbox")]
        for device in devices:
            hostname = device.name
            if device.device_type.manufacturer.name:
                manufacturer = device.device_type.manufacturer.name
            ip_address = device.primary_ip.address
            if "/" in ip_address:
                ip_address = ip_address.split("/")[0]
            host = {
                "hostname": hostname,
                "IP": ip_address,
                "manufacturer": manufacturer,
                "key": None,
                "source": "netbox",
            }
            hosts.append(host)
        update_sshmhosts(hosts, SSHMHOSTS)
        click.echo(f"Total synced hosts {len(devices)}")
    else:
        click.echo("No Netbox url or token set in SSHMCONFIG file")


cli.add_command(add)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(connect)
cli.add_command(manufacturers)
cli.add_command(config)
cli.add_command(sync)

if __name__ == "__main__":
    cli()
