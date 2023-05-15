import internetarchive
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("collection", type=str, help="Name of the collection")
parser.add_argument("output", type=str, help="Output file")
args = parser.parse_args()

search = internetarchive.search_items(args.collection)
i = 0
with open(args.output, "w") as fw:
    for item in search:
        i += 1
        if i % 1000 == 0:
            print("Records:", i)
        fw.write(item['identifier'])
        fw.write("\n")
