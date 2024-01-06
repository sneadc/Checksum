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
02a0f638674b70231739f47e3d12f2df036e85c0  README.md
f693ee230951abb2badb96145d73de383f0b8eed  checksum.ipynb
02dd284707f44919fba573dc9b4ef45f6b7253ac  pyproject.toml
```

Using. `SHA256`

```shell
checksum -a 256 *(.)
dfbb5cfdb419af3b53230ae3660bac0418d9da966cdb344375eb84696e3ec0b4  README.md
2f81f485b7ef71ff2ac2d500ff82c0cfdd9571edf59cc24a3737bf932ef68dd2  checksum.ipynb
c5b25a2068150ba97903c12e494d52dbc9c6c91b7ef697de7cc729f94d955290  pyproject.toml
```

Using. `MD5`

```shell
checksum -a md5 *(.)
b625e2c5325dbf7fc796b19b12e127a9  README.md
11c6df1ae02c19f090bfc3065c4c7677  checksum.ipynb
eba1e80977af31df86da99b6a5b93633  pyproject.toml
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
