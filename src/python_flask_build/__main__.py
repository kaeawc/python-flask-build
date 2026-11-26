"""Development server: `python -m python_flask_build`. Production runs gunicorn.conf.py."""

from __future__ import annotations

import logging

from python_flask_build.app import create_app
from python_flask_build.config import Config


def main() -> None:
    config = Config.from_env()
    app = create_app(config)
    logging.getLogger(__name__).info(
        "starting development server on %s:%d (debug=%s)", config.host, config.port, config.debug
    )
    app.run(host=config.host, port=config.port, debug=config.debug)


if __name__ == "__main__":
    main()
