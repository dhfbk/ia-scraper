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
parser.add_argument("--verbose", action="store_true", help="Verbose output")
args = parser.parse_args()

if not os.path.exists(args.output):
    os.mkdir(args.output)

i = 0
with open(args.input) as f:
    for line in f:
        i += 1
        if i % args.checkpoint == 0:
            print("INFO: checkpoint %d" % i)
        line = line.strip()
        prefix = line[:4]
        if not os.path.exists(os.path.join(args.output, prefix)):
            os.mkdir(os.path.join(args.output, prefix))
        outFileName = os.path.join(args.output, prefix, line)
        if os.path.exists(outFileName + "_djvu.txt"):
            if args.verbose:
                print("INFO: File %s already exists" % line)
            continue
        item = internetarchive.get_item(line)
        files = item.get_files()
        txtFileName = None
        for fi in files:
            if fi.format == "DjVuTXT":
                txtFileName = fi.name
        if txtFileName is None:
            print("ERR: File %s does not have text version" % line)
            continue

        if os.path.exists(os.path.join(args.output, prefix, txtFileName)):
            if args.verbose:
                print("INFO: File %s already exists" % line)
            continue

        if args.verbose:
            print("INFO: Downloading %s" % line)
        metadata = {}
        for k, v in item.metadata.items():
            metadata[k] = v
        with open(outFileName + ".json", "w") as fw:
            json.dump(metadata, fw)
        item.download(formats="DjVuTXT", destdir=os.path.join(args.output, prefix), no_directory=True)
        time.sleep(args.sleep)

# item = internetarchive.get_item("b20414973_0001")
# for k,v in item.metadata.items():
# files = item.get_files()
# item.download(formats="DjVuTXT")