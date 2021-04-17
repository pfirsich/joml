#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys


def main():
    if not os.path.isfile("run.py"):
        sys.exit("Execute this script from the tests/ directory")

    parser = argparse.ArgumentParser()
    parser.add_argument("binary")
    parser.add_argument("tests", nargs="*")
    args = parser.parse_args()

    pass_string = "\x1b[32mPASS\x1b[0m"
    fail_string = "\x1b[31mFAIL\x1b[0m"

    tests = args.tests
    if len(tests) == 0:
        tests = os.listdir(".")

    for test in tests:
        if os.path.isdir(test):
            res = subprocess.run(
                [args.binary, os.path.join(test, "input.joml")], capture_output=True
            )
            output_reference_path = os.path.join(test, "output.json")
            error_reference_path = os.path.join(test, "error")
            print(f"# {test}: ", end="")
            if os.path.isfile(output_reference_path):
                if res.returncode != 0:
                    print(f"{fail_string} (parsing failed)")
                    print(res.stderr, file=sys.stderr)
                else:
                    parsed = json.loads(res.stdout)
                    with open(output_reference_path) as f:
                        parsed_reference = json.load(f)
                    dump = lambda x: json.dumps(x, sort_keys=True)
                    if dump(parsed) != dump(parsed_reference):
                        print(f"{fail_string} (output differs)")
                        print(res.stdout, file=sys.stderr)
                    else:
                        print(pass_string)
            elif os.path.isfile(error_reference_path):
                if res.returncode == 0:
                    print(f"{fail_string} (parsing succeeded)")
                    print(res.stdout, file=sys.stderr)
                else:
                    with open(error_reference_path) as f:
                        error_reference = f.read()
                    if not error_reference in res.stderr.decode("utf-8"):
                        print(f"{fail_string} (wrong error)")
                        print(res.stderr, file=sys.stderr)
                    else:
                        print(pass_string)

            else:
                print(fail_string)
                sys.exit(
                    f"Neither output.json nor error are present for testcase '{test}'"
                )


if __name__ == "__main__":
    main()
