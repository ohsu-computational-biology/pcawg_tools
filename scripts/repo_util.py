#!/usr/bin/env python

import os
import re
import json
import argparse
import subprocess
import shutil
from nebula.dag import Target, TargetFile
from nebula.docstore import FileDocStore

def run_copy(docstore, out_docstore):
    doc = FileDocStore(file_path=docstore)

    out_doc = FileDocStore(file_path=out_docstore)

    for id, entry in doc.filter():
        if out_doc.get(id) is None:
            print "copy", id
            out_doc.put(id, entry)
            if doc.exists(entry):
                src_path = doc.get_filename(entry)
                out_doc.create(entry)
                dst_path = out_doc.get_filename(entry)
                shutil.copy(src_path, dst_path)
                out_doc.update_from_file(entry)
        else:
            #print "skip", id, doc.size(entry), out_doc.size(entry)
            if doc.size(entry) != out_doc.size(entry):
                print "mismatch", id


def run_errors(docstore):
    doc = FileDocStore(file_path=docstore)

    for id, entry in doc.filter():
        if entry.get('state', '') == 'error':
            if 'provenance' in entry:
                print "tool:", entry['provenance']['tool_id']
                print "-=-=-=-=-=-=-"
            print entry['job']['stdout'] #entry.get("stderr", )
            print "-------------"
            print entry['job']['stderr'] #entry.get("stderr", )
            print "-=-=-=-=-=-=-"

def run_get(docstore, uuid, outpath):
    doc = FileDocStore(file_path=docstore)
    print doc.get_filename(Target(uuid=uuid))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--docstore", help="DocStore", required=True)
    subparsers = parser.add_subparsers(title="subcommand")

    parser_query = subparsers.add_parser('copy')
    parser_query.set_defaults(func=run_copy)
    parser_query.add_argument("out_docstore", help="DocStore")

    parser_query = subparsers.add_parser('errors')
    parser_query.set_defaults(func=run_errors)

    args = parser.parse_args()
    func = args.func

    vargs = vars(args)
    del vargs['func']

    func(**vargs)
