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

    green = lambda x: f"\x1b[32m{x}\x1b[0m"
    red = lambda x: f"\x1b[31m{x}\x1b[0m"
    pass_string = green("PASS")
    fail_string = red("FAIL")

    tests = args.tests
    if len(tests) == 0:
        tests = os.listdir(".")

    total_test_count = 0
    failed_tests = []

    def fail(test, message, debug=None):
        print(f"{fail_string} ({message})")
        if debug:
            print(debug, file=sys.stderr)
        failed_tests.append(test)

    for test in tests:
        if os.path.isdir(test):
            total_test_count += 1
            res = subprocess.run(
                [args.binary, os.path.join(test, "input.joml")], capture_output=True
            )
            output_reference_path = os.path.join(test, "output.json")
            error_reference_path = os.path.join(test, "error")
            print(f"# {test}: ", end="")
            if os.path.isfile(output_reference_path):
                if res.returncode != 0:
                    fail("parsing failed", res.stderr)
                else:
                    parsed = json.loads(res.stdout)
                    with open(output_reference_path) as f:
                        parsed_reference = json.load(f)
                    dump = lambda x: json.dumps(x, sort_keys=True)
                    if dump(parsed) != dump(parsed_reference):
                        fail("output differs", res.stdout)
                    else:
                        print(pass_string)
            elif os.path.isfile(error_reference_path):
                if res.returncode == 0:
                    fail("parsing succeeded", res.stdout)
                else:
                    with open(error_reference_path) as f:
                        error_reference = f.read()
                    if not error_reference in res.stderr.decode("utf-8"):
                        fail("wrong error", res.stderr)
                    else:
                        print(pass_string)

            else:
                print(fail_string)
                sys.exit(f"Neither output.json nor error are present for test '{test}'")

    if failed_tests:
        print(
            "Failed {} of {} total tests:".format(len(failed_tests), total_test_count)
        )
        for test in failed_tests:
            print(test)
    else:
        print("All tests passed")


if __name__ == "__main__":
    main()
