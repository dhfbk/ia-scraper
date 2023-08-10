import internetarchive
import argparse
import os
import json
import time

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("input", type=str, help="Input file")
parser.add_argument("output", type=str, help="Output folder")
parser.add_argument("--sleep", type=float, help="Sleep time between downloads", default=4.0)
parser.add_argument("--checkpoint", type=int, help="Amount of downloads for notification", default=100)
parser.add_argument("--num_attempts", type=int, help="Number of attempts to download an item", default=5)
parser.add_argument("--max_depth", type=int, help="Maximum depth for recursion", default=3)
parser.add_argument("--verbose", action="store_true", help="Verbose output")
args = parser.parse_args()

def download(args, line, depth):
    prefix = line[:4]
    if not os.path.exists(os.path.join(args.output, prefix)):
        os.mkdir(os.path.join(args.output, prefix))
    outFileName = os.path.join(args.output, prefix, line)
    if os.path.exists(outFileName + "_djvu.txt"):
        if args.verbose:
            print("INFO: File %s already exists" % line)
        return
    gotItem = False
    attempts = 0
    while not gotItem and attempts < args.num_attempts:
        try:
            item = internetarchive.get_item(line)
            gotItem = True
        except:
            attempts += 1
            print("ERR: Item %s cannot be downloaded, sleeping..." % line)
            time.sleep(args.sleep)
    if not gotItem:
        return
    files = item.get_files()
    txtFileName = None
    for fi in files:
        if fi.format == "DjVuTXT":
            txtFileName = fi.name
    if txtFileName is None:
        print("ERR: File %s does not have text version" % line)
        if depth >= args.max_depth:
            print("ERR: Max depth reached")
        else:
            if args.verbose:
                print("INFO: Going deep for %s" % line)
            metadata = {}
            metadata['od_type'] = "collection"
            metadata['od_files'] = []
            for k, v in item.metadata.items():
                metadata[k] = v
            try:
                search = internetarchive.search_items(line)
                for subItem in search:
                    if subItem['identifier'] == line:
                        continue
                    metadata['od_files'].append(subItem['identifier'])
                    download(args, subItem['identifier'], depth + 1)
                if args.verbose:
                    print("INFO: Saving JSON for %s" % line)
                with open(outFileName + ".json", "w") as fw:
                    json.dump(metadata, fw)
            except:
                print("ERR: problem in download, continuing...")
                time.sleep(args.sleep)
        return

    if os.path.exists(os.path.join(args.output, prefix, txtFileName)):
        if args.verbose:
            print("INFO: File %s already exists" % line)
        return

    if args.verbose:
        print("INFO: Downloading %s" % line)
    metadata = {}
    for k, v in item.metadata.items():
        metadata[k] = v
    with open(outFileName + ".json", "w") as fw:
        json.dump(metadata, fw)
    downloaded = False
    attempts = 0
    while not downloaded and attempts < args.num_attempts:
        try:
            item.download(formats="DjVuTXT", destdir=os.path.join(args.output, prefix), no_directory=True)
            downloaded = True
        except:
            attempts += 1
            print("ERR: File %s cannot be downloaded, sleeping..." % line)
            time.sleep(args.sleep)
    time.sleep(args.sleep)

if not os.path.exists(args.output):
    os.mkdir(args.output)

depth = 0
i = 0
with open(args.input) as f:
    for line in f:
        i += 1
        if i % args.checkpoint == 0:
            print("INFO: checkpoint %d" % i)
        line = line.strip()
        try:
            download(args, line, depth)
        except:
            print("ERR: problem in download, continuing...")
            time.sleep(args.sleep)

# item = internetarchive.get_item("b20414973_0001")
# for k,v in item.metadata.items():
# files = item.get_files()
# item.download(formats="DjVuTXT")
