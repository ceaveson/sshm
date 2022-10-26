from genericpath import exists
import yaml
import click
from yaml.loader import SafeLoader
import os

hosts = []

try:
    with open('.sshmanagerhosts.yaml','r') as f:
        hosts = list(yaml.load_all(f, Loader=SafeLoader))
        for key, host in enumerate(hosts):
            host["key"] = key
except:
    pass

@click.group()
def cli():
    pass

@click.command()
def add():
    hostname = click.prompt("Hostname")
    IP = click.prompt("IP Address")
    click.echo(f"Hostname: {hostname}")
    click.echo(f"IP Address: {IP}")
    confirm = f"""Are these details correct?
    Hostname {hostname}
    IP Address {IP}
    """
    if click.confirm(confirm):
        host = {'hostname': hostname, 'IP': IP}
        hosts.append(host)
        for host in hosts:
            host.pop('key')
        with open('.sshmanagerhosts.yaml', 'w') as f:
            f.write(yaml.dump_all(hosts))
        click.echo("added")

@click.command()
def delete():
    click.echo("deleting...")

@click.command()
def show():
    for host in hosts:
        click.echo(f"{host['key']} - {host['hostname']} - {host['IP']}")

@click.command()
@click.argument('hostname')
def connect(hostname):
    for host in hosts:
        if host['hostname'] == hostname:
            os.system(f"ssh {host['IP']}")


cli.add_command(add)
cli.add_command(delete)
cli.add_command(show)
cli.add_command(connect)

if __name__ == "__main__":
    cli()