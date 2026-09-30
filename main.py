import argparse
from dotenv import load_dotenv

from agent import run_agent
from tools import TOOLS, make_tool_functions

load_dotenv()

SOURCES = ("mock", "inspire")

parser = argparse.ArgumentParser(description="Scientific paper metadata assistant")
parser.add_argument("--source", choices=SOURCES, default="inspire", help="Data source: mock (local) or inspire (live API), default: inspire")
parser.add_argument("question", nargs="?", default="Find the most cited paper about neutrino oscillations and tell me its full details.")
args = parser.parse_args()

if args.source == "mock":
    from data import mock as data_module
else:
    from data import inspire as data_module

tool_functions = make_tool_functions(data_module)

print(f"Question: {args.question}")
print(f"Source: {args.source}\n")

answer = run_agent(args.question, tool_functions, TOOLS)
print(f"\nAnswer:\n{answer}")
