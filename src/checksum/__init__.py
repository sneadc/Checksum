from __future__ import annotations

import os
import re
import sys
import hashlib
import logging
import argparse

from select import select
from typing import Any

from .__version__ import __version__


def hasher(
    file: str, algorithm: str = "sha256", blocksize: int = 1048576
) -> Any:
    buff = bytearray(blocksize)
    pbuf = memoryview(buff)
    size = os.stat(file).st_size
    algo = getattr(hashlib, algorithm)()
    with open(file, mode="rb") as f:
        while size:
            read = f.readinto(buff)
            algo.update(pbuf[:read])
            size -= read
    return algo.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=__name__,
        description="Print or check checksums using; SHA1, SHA256, MD5 ...",
        epilog="With no FILE, or when FILE is -, read standard input.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="The name of the file to hash.",
        metavar="FILE",
    )
    parser.add_argument(
        "-a",
        "--algorithm",
        dest="algorithm",
        choices=["1", "224", "256", "384", "512", "md5"],
        default="1",
        help="1, 224, 256, 384, 512, md5. (default: %(default)s)",
        metavar="S",
    )
    parser.add_argument(
        "-B",
        "--blocksize",
        dest="blocksize",
        default=1024**2,
        type=int,
        help="read up to N bytes at a time.",
        metavar="N",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="read checksums from the FILEs and check them",
    )
    parser.add_argument(
        "--ignore-missing",
        dest="ignore_missing",
        action="store_true",
        help="don't fail or report status for missing files.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="don't print OK for each successfully verified file.",
    )
    parser.add_argument(
        "--status",
        action="store_false",
        help="don't output anything, status code shows success.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero for improperly formatted checksum lines.",
    )
    parser.add_argument(
        "--tag",
        action="store_true",
        help="create a BSD-style checksum",
    )
    parser.add_argument(
        "-w",
        "--warn",
        action="store_true",
        help="warn about improperly formatted checksum lines.",
    )
    parser.add_argument(
        "-z",
        "--zero",
        action="store_true",
        help="end each output line with NUL, not newline.",
    )
    parser.add_argument(
        "-b",
        "--binary",
        action="store_true",
        help="* does nothing, added for compatibility.",
    )
    parser.add_argument(
        "-t",
        "--text",
        action="store_true",
        help="* does nothing, added for compatibility.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args(argv)

    end = "\0" if args.zero else "\n"
    pattern = (
        r"(^(?P<alg>[A-Z]+[0-9]+)\s+\((?P<pth>[^)]+)\) = (?P<hsh>[a-z0-9]+)$)"
        r"|(^(?P<hash>[a-z0-9]{20,})\s[\* ](?P<file>.+)$)"
    )
    reobj = re.compile(pattern, re.MULTILINE)

    logging.getLogger(parser.prog).setLevel(0 if args.status else "ERROR")

    if args.algorithm in ["1", "224", "256", "384", "512"]:
        args.algorithm = "sha" + args.algorithm

    try:
        if select([sys.stdin], [], [], 0.0)[0]:
            args.files = [0]
    except (ValueError, IndexError):
        # Not using a terminal?
        ...

    rc = 0
    for file in args.files:
        if args.check:
            lineno = 0
            unread = 0
            failures = 0
            illformated = 0
            try:
                with open(file) as f:
                    lines = f.readlines()
                for line in lines:
                    lineno += 1
                    status = "FAILED"

                    match = reobj.search(line)
                    if not match:
                        illformated += 1
                        if args.warn:
                            logging.getLogger(parser.prog).warning(
                                f"{file}: {lineno}: improperly formatted"
                                " checksum line"
                            )
                        continue

                    groups = match.groupdict()
                    checksum = (
                        groups["hsh"] if groups["hsh"] else groups["hash"]
                    )
                    filename = (
                        groups["pth"] if groups["pth"] else groups["file"]
                    )
                    if groups["alg"]:
                        args.algorithm = groups["alg"]

                    if os.path.exists(filename):
                        computed = hasher(
                            filename, args.algorithm.lower(), args.blocksize
                        )
                        if computed != checksum:
                            failures += 1
                    elif not args.ignore_missing:
                        logging.getLogger(parser.prog).error(
                            f"{filename}: No such file or directory"
                        )
                        computed = None
                        status += " open or read"
                        unread += 1
                    else:
                        continue

                    status = "OK" if computed == checksum else status
                    if args.status and (not args.quiet or status != "OK"):
                        print(f"{filename}: {status}")

                if illformated:
                    logging.getLogger(parser.prog).warning(
                        "%s line is improperly formatted", illformated
                    )
                if unread:
                    logging.getLogger(parser.prog).warning(
                        "%s listed file could not be read", unread
                    )
                if failures:
                    logging.getLogger(parser.prog).warning(
                        "%s computed checksums did NOT match", failures
                    )

                if args.strict:
                    rc += illformated
                rc += failures + unread
            except FileNotFoundError as err:
                logging.getLogger(parser.prog).warning(
                    "%s: %s", err.filename, err.strerror
                )
                rc += 1
        else:
            if os.path.isdir(file):
                logging.getLogger(parser.prog).warning(
                    f"{file}: Is a directory"
                )
                continue

            computed = hasher(file, args.algorithm.lower(), args.blocksize)
            file = file if isinstance(file, str) else "-"
            if args.tag:
                print(
                    f"{args.algorithm.upper()} ({file}) = {computed}", end=end
                )
            else:
                print(f"{computed}  {file}", end=end)

    return rc
