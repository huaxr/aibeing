#!/usr/bin/env python
import argparse
from service import ws, greeting
from interact.llm.vector import script

parser = argparse.ArgumentParser()
parser.add_argument('--type', help='service type: ws, http', default='ws')
parser.add_argument('--port', help='service port', default=None)

args = parser.parse_args()

if __name__ == '__main__':
    if args.type == 'ws':
        ws.startapp(args.port)
    if args.type == 'greeting':
        greeting.main()
    if args.type == 'vector':
        script.main()