"""
An mitmproxy adblock script!
(Required python3 modules: re and adblockparser)

(c) 2015 epitron
2018 ar0xa update for python3
"""

import re
from glob import glob
from mitmproxy.script import concurrent
from mitmproxy import http
from mitmproxy import ctx

sys.path.append('/usr/local/lib/python3.4/dist-packages/')
from adblockparser import AdblockRules

def combined(filenames):
  '''
  Open and combine many files into a single generator which returns all
  of their lines. (Like running "cat" on a bunch of files.)
  '''
  for filename in filenames:
    with open(filename) as file:
      for line in file:
        yield line


def load_rules(blocklists=None):
  rules = AdblockRules(
    combined(blocklists),
#    use_re2=True,
    max_mem=512*1024*1024
    # supported_options=['script', 'domain', 'image', 'stylesheet', 'object']
  )

  return rules

def load(l):
    global rules
    blocklists = glob("easylists/*")
    if len(blocklists) == 0:
      ctx.log("Error, no blocklists found in 'easylists/'. Please run the 'update-blocklists' script.")
      raise SystemExit

    else:
      ctx.log("* Loading adblock rules...")
      for list in blocklists:
        ctx.log("  |_ %s" % list)

    rules = load_rules(blocklists)
    ctx.log("")
    ctx.log("* Done! Proxy server is ready to go!")

IMAGE_MATCHER      = re.compile(r"\.(png|jpe?g|gif)$")
SCRIPT_MATCHER     = re.compile(r"\.(js)$")
STYLESHEET_MATCHER = re.compile(r"\.(css)$")

#entry point
#@concurrent
def request(flow):
    req = flow.request
    if req.host is not None:
        # accept = flow.request.headers["Accept"]
        # context.log("accept: %s" % flow.request.accept)

        options = {'domain': req.host}

        if IMAGE_MATCHER.search(req.path):
            options["image"] = True
        elif SCRIPT_MATCHER.search(req.path):
            options["script"] = True
        elif STYLESHEET_MATCHER.search(req.path):
            options["stylesheet"] = True

        if rules.should_block(req.url, options):
            #ctx.log.info("vvvvvvvvvvvvvvvvvvvv BLOCKED vvvvvvvvvvvvvvvvvvvvvvvvvvv")
            #ctx.log.info("accept: %s" % req.headers.get("Accept"))
            #ctx.log.info("blocked-host: %s" % req.url)
            #ctx.log.info("^^^^^^^^^^^^^^^^^^^^ BLOCKED ^^^^^^^^^^^^^^^^^^^^^^^^^^^")

            flow.response = http.HTTPResponse.make(
                200,
                b"Blocked",
                {"Content-Type": "text/html"}
            )
        #else:
        #    ctx.log.info("No blocked url: %s" % req.host)


