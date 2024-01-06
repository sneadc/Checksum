from __future__ import annotations

import sys

from . import main


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except KeyboardInterrupt:
        sys.exit(rc)
    except Exception as e:
        print("Error: %s" % e, file=sys.stderr)
    sys.exit(rc)
