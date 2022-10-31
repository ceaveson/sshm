from sshm import create_hosts_dict, update_sshmhosts

sshmhosts_file = ".sshmhosts.yaml"

sshmhosts_example = """IP: 127.0.0.1
hostname: loopback
---
IP: 1.1.1.1
hostname: host1
---
IP: 2.2.2.2
hostname: host2
"""


def test_create_hosts_dict(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / sshmhosts_file
    p.write_text(sshmhosts_example)
    hosts = create_hosts_dict(p)
    host = [i for i in hosts if "loopback" in i["hostname"]][0]

    assert len(hosts) == 3 and host["IP"] == "127.0.0.1"

def test_update_sshmhosts(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / sshmhosts_file
    p.write_text(sshmhosts_example)
    
    hosts = [{'IP': '1.0.0.127', 'hostname': 'not_loopback', 'key': 0}, {'IP': '3.3.3.3', 'hostname': 'host3', 'key': 1}, {'IP': '4.4.4.4', 'hostname': 'host4', 'key': 2}]
    update_sshmhosts(hosts, p)

    f = open(p)
    flist = f.readlines()
    assert len(flist) == 8 and [i for i in flist if "hostname: not_loopback" in i][0]
        