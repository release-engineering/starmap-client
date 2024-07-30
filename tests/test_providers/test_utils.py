# SPDX-License-Identifier: GPL-3.0-or-later
# The tests below were adapted from Kobo's RPMLib:
# https://github.com/release-engineering/kobo/blob/master/tests/test_rpmlib.py
import unittest

from starmap_client.providers.utils import get_image_name, parse_nvr


class TestNVR(unittest.TestCase):
    def test_parse_nvr_success(self) -> None:
        self.assertEqual(
            parse_nvr("net-snmp-5.3.2.2-5.el5"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch=""),
        )
        self.assertEqual(
            parse_nvr("1:net-snmp-5.3.2.2-5.el5"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch="1"),
        )
        self.assertEqual(
            parse_nvr("net-snmp-1:5.3.2.2-5.el5"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch="1"),
        )
        self.assertEqual(
            parse_nvr("net-snmp-5.3.2.2-5.el5:1"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch="1"),
        )
        self.assertEqual(
            parse_nvr("/net-snmp-5.3.2.2-5.el5:1"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch="1"),
        )
        self.assertEqual(
            parse_nvr("/1:net-snmp-5.3.2.2-5.el5"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch="1"),
        )
        self.assertEqual(
            parse_nvr("foo/net-snmp-5.3.2.2-5.el5:1"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch="1"),
        )
        self.assertEqual(
            parse_nvr("foo/1:net-snmp-5.3.2.2-5.el5"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch="1"),
        )
        self.assertEqual(
            parse_nvr("/foo/bar/net-snmp-5.3.2.2-5.el5:1"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch="1"),
        )
        self.assertEqual(
            parse_nvr("/foo/bar/1:net-snmp-5.3.2.2-5.el5"),
            dict(name="net-snmp", version="5.3.2.2", release="5.el5", epoch="1"),
        )

        # test for name which contains the version number and a dash
        self.assertEqual(
            parse_nvr("openmpi-1.10-1.10.2-2.el6"),
            dict(name="openmpi-1.10", version="1.10.2", release="2.el6", epoch=""),
        )

    def test_parse_nvr_invalid(self) -> None:
        self.assertRaises(RuntimeError, parse_nvr, "net-snmp")
        self.assertRaises(RuntimeError, parse_nvr, "net-snmp-5.3.2.2-1:5.el5")
        self.assertRaises(RuntimeError, parse_nvr, "1:net-snmp-5.3.2.2-5.el5:1")
        self.assertRaises(RuntimeError, parse_nvr, "1:net-snmp-1:5.3.2.2-5.el5")
        self.assertRaises(RuntimeError, parse_nvr, "net-snmp-1:5.3.2.2-5.el5:1")
        self.assertRaises(RuntimeError, parse_nvr, "1:net-snmp-1:5.3.2.2-5.el5:1")

    def test_get_image_name(self) -> None:
        self.assertEqual(get_image_name("net-snmp-5.3.2.2-5.el5"), "net-snmp")
        self.assertEqual(get_image_name("1:net-snmp-5.3.2.2-5.el5"), "net-snmp")
        self.assertEqual(get_image_name("net-snmp-1:5.3.2.2-5.el5"), "net-snmp")
        self.assertEqual(get_image_name("net-snmp-5.3.2.2-5.el5:1"), "net-snmp")
        self.assertEqual(get_image_name("/net-snmp-5.3.2.2-5.el5:1"), "net-snmp")
        self.assertEqual(get_image_name("/1:net-snmp-5.3.2.2-5.el5"), "net-snmp")
        self.assertEqual(get_image_name("foo/net-snmp-5.3.2.2-5.el5:1"), "net-snmp")
        self.assertEqual(get_image_name("foo/1:net-snmp-5.3.2.2-5.el5"), "net-snmp")
        self.assertEqual(get_image_name("/foo/bar/net-snmp-5.3.2.2-5.el5:1"), "net-snmp")
        self.assertEqual(get_image_name("/foo/bar/1:net-snmp-5.3.2.2-5.el5"), "net-snmp")
        self.assertEqual(
            get_image_name("openmpi-1.10-1.10.2-2.el6"),
            "openmpi-1.10",
        )
        self.assertEqual(get_image_name(None), "")
