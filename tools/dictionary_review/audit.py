"""Audit every canonical tag; emit pending work without treating legacy text as verified."""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from rules import descriptive, glossary, characters, copyrights, display_original

ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = {"0":"general", "1":"artist", "3":"copyright", "4":"character", "5":"meta",
 "7":"general", "8":"artist", "9":"contributor", "10":"copyright", "11":"character",
 "12":"species", "14":"meta", "15":"lore"}

def read_labels(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row[0]:row[-1].strip() for row in csv.reader(stream) if len(row)>1}

def run(output, apply=False):
    output.mkdir(parents=True,exist_ok=True)
    dictionary=ROOT/"translate/Ru_translated.csv"
    labels=read_labels(dictionary)
    reviewed={}; inventory=[]
    for filename in ["danbooru_e621_merged.csv", "extra-quality-tags.csv"]:
        with (ROOT/"tags"/filename).open(encoding="utf-8",newline="") as stream:
            for row in csv.reader(stream):
                if len(row)<4:continue
                tag,code,count,aliases=row[:4]
                category="quality" if filename.startswith("extra") else CATEGORIES.get(code,"unknown")
                label=labels.get(tag,"")
                expected,rule=(None,None)
                if category in {"general","meta","species","lore","quality"}:
                    expected,rule=descriptive(tag)
                if category=="character" and tag in characters:
                    expected,rule=characters[tag],"character-name"
                if category=="copyright" and tag in copyrights:
                    expected,rule=copyrights[tag],"work-title"
                if expected is not None:
                    reviewed[tag]=expected
                    status="reviewed" if label==expected else "correction_available"
                elif category in {"artist","contributor"}:
                    status="preserve_handle";rule="never_translate_handle"
                elif category=="character" and not label:
                    status="original_name_preserved";rule="no_verified_localized_name"
                elif category=="copyright" and label in {"",display_original(tag)}:
                    status="original_title_preserved";rule="not_a_verified_localized_title"
                elif not re.search(r"[A-Za-zА-Яа-яЁё]",tag):
                    status="preserve_symbol";rule="never_translate_symbol"
                else:
                    status="needs_review" if label else "missing_translation"
                issues=[]
                if status in {"needs_review","missing_translation"}:
                    if label and re.search(r"[A-Za-z]",label) and re.search(r"[А-Яа-яЁё]",label):issues.append("mixed_scripts")
                    if "_" in label:issues.append("underscore_in_label")
                    if tag in label and label!=tag:issues.append("repeats_tag")
                inventory.append({"tag":tag,"category":category,"count":int(count) if count.isdigit() else 0,
                    "translation":label,"status":status,"rule":rule or "","issues":";".join(issues)})
    if apply:
        labels.update(reviewed)
        temporary=dictionary.with_suffix(".csv.tmp")
        with temporary.open("w",encoding="utf-8",newline="") as stream:
            csv.writer(stream,lineterminator="\n").writerows(labels.items())
        temporary.replace(dictionary)
        for row in inventory:
            if row["status"]=="correction_available":row["translation"]=reviewed[row["tag"]];row["status"]="reviewed"
    fields=["tag","category","count","translation","status","rule","issues"]
    inventory.sort(key=lambda row:row["count"],reverse=True)
    for name,items in [("inventory.csv",inventory),("pending.csv",[row for row in inventory if row["status"] in {"needs_review","missing_translation","correction_available"}])]:
        with (output/name).open("w",encoding="utf-8-sig",newline="") as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(items)
    summary={"total":len(inventory),"statuses":dict(Counter(row["status"] for row in inventory)),
        "by_category":{category:dict(Counter(row["status"] for row in inventory if row["category"]==category)) for category in sorted({row["category"] for row in inventory})}}
    (output/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,required=True);parser.add_argument("--apply",action="store_true")
    args=parser.parse_args();run(args.output,args.apply)
