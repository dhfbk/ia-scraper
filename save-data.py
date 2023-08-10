import argparse
import glob
import os
import json
import re
import shutil

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--input", type=str, help="Input folders", required=True, nargs="+")
parser.add_argument("--output", type=str, help="Output folder", required=True)
parser.add_argument("--verbose", action="store_true", help="Verbose output")
parser.add_argument("--splits", type=int, help="Number of split, default 10", default=10)
parser.add_argument("--limit", type=int, help="Number of documents, default 0 (all)", default=0)
parser.add_argument("--checkpoint", type=int, help="Amount of downloads for notification", default=1000)
args = parser.parse_args()

folders = args.input
verbose = args.verbose
splits = args.splits
output = args.output
limit = args.limit
checkpoint = args.checkpoint

if not os.path.exists(output):
    os.mkdir(output)

buffers = []
for index in range(splits):
    os.mkdir(os.path.join(output, str(index)))
    os.mkdir(os.path.join(output, str(index), "data"))
    indexFile = os.path.join(output, str(index), "metadata.tsv")
    buffers.append(open(indexFile, "w"))

def getValue(l, k, separator=","):
    r = ""
    if k in l:
        r = l[k]
    if type(r) == list:
        r = ", ".join(r)
    r = r.replace("\t", " ")
    return r

savedCount = 0
skippedCount = 0

thisIndex = 0
for f in folders:
    print(f"FOLDER: {f}")
    for file in glob.glob(os.path.join(f, "*", "*.json")):
        with open(file) as f:
            data = json.load(f)
            dirname = os.path.dirname(file)
            if "identifier" not in data:
                continue
            identifier = data['identifier']
            identifier = re.sub(r"\..*", "", identifier)
            djvufilename = identifier + "_djvu.txt"
            djvufilepath = os.path.join(dirname, djvufilename)
            found = True
            if not os.path.exists(djvufilepath):
                found = False
                for txtfile in glob.glob(os.path.join(dirname, "*.txt")):
                    bn = os.path.basename(txtfile)
                    bn = bn[0:len(bn) - 9]
                    bn = re.sub(r"[^A-Za-z0-9]", "", bn)
                    if bn == identifier:
                        found = True
                        djvufilepath = txtfile
                        break
                    if bn == identifier.replace("tobacco_", ""):
                        found = True
                        djvufilepath = txtfile
                        break
                if not found and verbose:
                    print(f"ERR: file {djvufilepath} does not exist ({file})")
            if not found:
                skippedCount += 1
                continue

            savedCount += 1

            thisIndex += 1
            thisSplit = thisIndex % splits
            if verbose:
                print(f"INFO: Processing {identifier}...")

            outFile = os.path.join(output, str(thisSplit), "data", identifier)
            shutil.copyfile(djvufilepath, outFile)

            buffers[thisSplit].write(identifier)
            buffers[thisSplit].write("\t")
            buffers[thisSplit].write(getValue(data, "date"))
            buffers[thisSplit].write("\t")
            buffers[thisSplit].write(getValue(data, "creator"))
            buffers[thisSplit].write("\t")
            buffers[thisSplit].write(getValue(data, "title"))
            buffers[thisSplit].write("\t")
            buffers[thisSplit].write(getValue(data, "subject"))
            buffers[thisSplit].write("\t")
            buffers[thisSplit].write(getValue(data, "identifier-access"))
            buffers[thisSplit].write("\t")
            buffers[thisSplit].write(getValue(data, "collection"))
            buffers[thisSplit].write("\n")

        if thisIndex % checkpoint == 0:
            print("INFO: checkpoint %d" % thisIndex)
            
        if limit > 0 and thisIndex >= limit:
            break

for b in buffers:
    b.close()

print(f"Saved files: {savedCount}")
print(f"Skipped files: {skippedCount}")
