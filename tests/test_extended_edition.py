"""Tests for preserving movie cut information in generated filenames."""

import ast
import pathlib
import re
import types
import unittest


def load_edition_method():
    # Test the real method without initializing the app's network services.
    source = pathlib.Path(__file__).parents[1] / "app/media/meta/_base.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MetaBase")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "get_edtion_string")
    namespace = {"re": re, "MediaType": types.SimpleNamespace(MOVIE="movie")}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), "exec"), namespace)
    return namespace["get_edtion_string"]


class ExtendedEditionTest(unittest.TestCase):
    def test_markers_and_existing_technical_details(self):
        method = load_edition_method()
        for name in ("Film.2001.Extended.UHD.mkv", "Film.2001.EXTENDED.EDITION.mkv", "电影.2001.加长版.mkv", "電影.2001.加長版.mkv"):
            with self.subTest(name=name):
                media = types.SimpleNamespace(org_string=name, type="movie", resource_type="Blu-ray", resource_effect="HDR10")
                self.assertEqual(method(media), "加长版 Blu-ray HDR10")

    def test_other_titles_and_tv_are_not_marked(self):
        method = load_edition_method()
        for name, media_type in (("Film.2001.BluRay.mkv", "movie"), ("Film.2001.Unextended.mkv", "movie"), ("Show.Extended.S01.mkv", "tv"), (None, "movie")):
            with self.subTest(name=name, media_type=media_type):
                media = types.SimpleNamespace(org_string=name, type=media_type, resource_type="Blu-ray", resource_effect=None)
                self.assertEqual(method(media), "Blu-ray")


if __name__ == "__main__":
    unittest.main()
