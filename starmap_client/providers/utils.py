# SPDX-License-Identifier: GPL-3.0-or-later
# The functions below were adapted from Kobo's RPMLib:
# https://github.com/release-engineering/kobo/blob/master/kobo/rpmlib.py
import logging
from typing import Dict, Optional, Tuple

log = logging.getLogger(__name__)


def split_nvr_epoch(nvre: str) -> Tuple[str, str]:
    """
    Split nvre to N-V-R and E.

    :param nvre: E:N-V-R or N-V-R:E string
    :return: (N-V-R, E)
    """
    if ":" in nvre:
        log.debug("Splitting NVR and Epoch")
        if nvre.count(":") != 1:
            raise RuntimeError(f"Invalid NVRE: {nvre}")

        nvr, epoch = nvre.rsplit(":", 1)
        if "-" in epoch:
            if "-" not in nvr:
                # switch nvr with epoch
                nvr, epoch = epoch, nvr
            else:
                # it's probably N-E:V-R format, handle it after the split
                nvr, epoch = nvre, ""
    else:
        log.debug("No epoch to split")
        nvr, epoch = nvre, ""

    return nvr, epoch


def parse_nvr(nvre: str) -> Dict[str, str]:
    """
    Split N-V-R into a dictionary.

    :param nvre: N-V-R:E, E:N-V-R or N-E:V-R string
    :return: {name, version, release, epoch}
    """
    log.debug("Parsing NVR")
    if "/" in nvre:
        nvre = nvre.split("/")[-1]

    nvr, epoch = split_nvr_epoch(nvre)

    log.debug("Splitting NVR parts")
    nvr_parts = nvr.rsplit("-", 2)
    if len(nvr_parts) != 3:
        raise RuntimeError(f"Invalid NVR: {nvr}")

    # parse E:V
    if epoch == "" and ":" in nvr_parts[1]:
        log.debug("Parsing E:V")
        epoch, nvr_parts[1] = nvr_parts[1].split(":", 1)

    # check if epoch is empty or numeric
    if epoch != "":
        try:
            int(epoch)
        except ValueError:
            raise RuntimeError(f"Invalid epoch '{epoch}' in '{nvr}'")

    result = dict(zip(["name", "version", "release"], nvr_parts))
    result["epoch"] = epoch
    return result


def get_image_name(image: Optional[str]) -> str:
    """Retrieve the name from NVR."""
    if not image:
        return ""
    nvr = parse_nvr(image)
    return nvr.get("name", "")
