"""Command line front end for viewscope.build_bundle, runnable from a checkout."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from viewscope.build_bundle import main  # noqa: E402

raise SystemExit(main())
