# Checksum

A drop in replacement for GNU SHA{1, 224, 256, 512}sum to compute and check SHA, and MD5 message digest.

Runs significantly faster on the M1 in comparison to the perl versions which ship with MacOS, and available via GNU.

## Installation

```shell
pip install git+https://github.com/sneadc/checksum
```

## Usage

```none
usage: checksum [-h] [-a S] [-B N] [-c] [--ignore-missing] [-q] [--status]
                [--strict] [--tag] [-w] [-z] [-b] [-t] [-v]
                [FILE ...]

Print or check checksums using; SHA1, SHA256, MD5 ...

positional arguments:
  FILE                 The name of the file to hash.

options:
  -h, --help           show this help message and exit
  -a S, --algorithm S  1, 224, 256, 384, 512, md5. (default: 1)
  -B N, --blocksize N  read up to N bytes at a time.
  -c, --check          read checksums from the FILEs and check them
  --ignore-missing     don't fail or report status for missing files.
  -q, --quiet          don't print OK for each successfully verified file.
  --status             don't output anything, status code shows success.
  --strict             exit non-zero for improperly formatted checksum lines.
  --tag                create a BSD-style checksum
  -w, --warn           warn about improperly formatted checksum lines.
  -z, --zero           end each output line with NUL, not newline.
  -b, --binary         * does nothing, added for compatibility.
  -t, --text           * does nothing, added for compatibility.
  -v, --version        show program's version number and exit

With no FILE, or when FILE is -, read standard input.
```

Default. `SHA1`

```shell
checksum *(.)
721e9c281b1f0c22e06683cf895d7390b68d391f  README.md
ee82aa809414e5f9563eb3e512396280071b4de0  checksum.ipynb
8103c1bae9828dc2de155dde524717e8e3c5b4d7  pyproject.toml
```

Using. `SHA256`

```shell
checksum -a 256 *(.)
9b81b3d3aeb7f4f40bbb4c384d9d384b724ccd520014e12243cdb1fa77d06941  README.md
e63f71bd5f70cc82ddbcdd689f3a36e2870b70aa8c220bfb29bb3e53747cf36b  checksum.ipynb
ede91749ca2c36bd27c0581189eee17967a85e7b60a7724db6be609dfa26f72a  pyproject.toml
```

Using. `MD5`

```shell
checksum -a md5 *(.)
7a0254c0010f9889145fca9eeaa91778  README.md
ba8b33fa13c22b11de6774adb614283d  checksum.ipynb
bace454752bd3d1568660ea97a93fd35  pyproject.toml
```

Comparison with GNU `sha256sum`:

1. Sample file creation.

   ```shell
   $ dd if=/dev/zero of=large.bin bs=1G count=3
   3+0 records in
   3+0 records out
   3221225472 bytes (3.2 GB, 3.0 GiB) copied, 0.935256 s, 3.4 GB/s
   ```

1. Time with GNU `sha256sum`.

   ```shell
   $ time (sha256sum large.bin)
   305b66a59d15b252092fbda9d09711230c429f351897cbd430e7b55a35fd3b97  large.bin
   ( sha256sum large.bin; )  10.47s user 0.40s system 98% cpu 11.052 total
   ```

   ***<u>11.052</u>** seconds total.*

1. Time with `checksum`.

   ```shell
   $ time (checksum -a 256 large.bin)
   305b66a59d15b252092fbda9d09711230c429f351897cbd430e7b55a35fd3b97  large.bin
   ( checksum -a 256 large.bin; )  1.35s user 0.27s system 87% cpu 1.846 total
   ```

   ***<u>1.846</u>** seconds total.*

1. $$11.052 / 1.846 = 5.987$$

**5.987 times faster !!!**

## History

| Version | Notes   | Released   |
| ------- | ------- | ---------- |
| 0.1.0   | initial | 2023-12-25 |
