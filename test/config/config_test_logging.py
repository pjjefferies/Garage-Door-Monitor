""" Set-up Test History Logging and load logging configuration as log_test_cfg, boxed """

import logging
from os import makedirs, path
from typing import Any
from yaml import safe_load

from box import Box

from src.config.config_main import cfg
from test.config.config_test_main import test_cfg


def load_test_log_config() -> Box:
    """
    Load logging config as log_test_cfg
    Create logging folder if necessary
    """
    logging_config_path_filename: str = test_cfg.LOGGING.CONFIG_PATH

    try:
        with open(logging_config_path_filename, "r") as fp:
            log_config_dict: dict[str, Any] = safe_load(fp)  # YAML

        log_test_cfg: Box = Box(
            {**log_config_dict["base"]}, default_box=True, default_box_attr=None
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Log yaml configuration file not found in {cfg.path.log_config}"
        )

    makedirs(name=log_test_cfg.handler.log_file.folder, exist_ok=True)

    return log_test_cfg


log_test_cfg: Box = load_test_log_config()

log_fmt = logging.Formatter(fmt=log_test_cfg.format.simple, style="{")
logging.basicConfig(
    format=log_test_cfg.format.simple, style="{", datefmt=log_test_cfg.format.datefmt
)

history_test_logger: logging.Logger = logging.getLogger(
    "Garage Door Monitor History Test Logger"
)
history_test_logger.setLevel(level=log_test_cfg.level)
history_test_logger.propagate = False

if log_test_cfg.handler.test_history.enabled:
    # Set-up history test logging
    h_t_fh = logging.FileHandler(
        filename=path.join(
            log_test_cfg.handler.test_history.folder,
            log_test_cfg.handler.test_history.filename,
        )
    )
    h_t_fh.setLevel(level=log_test_cfg.handler.test_history.level)
    h_t_fh.setFormatter(fmt=log_fmt)
    history_test_logger.addHandler(hdlr=h_t_fh)
