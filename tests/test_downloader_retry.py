import ast
import pathlib
import threading
import types
import unittest
from unittest.mock import Mock


def load_transfer():
    path = pathlib.Path(__file__).parents[1] / "app/downloader/downloader.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == "Downloader")
    method = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == "transfer")
    scope = {"lock": threading.Lock(), "log": Mock(), "PT_TAG": "NASTOOL",
             "ModuleConf": types.SimpleNamespace(RMT_MODES={"link": "link"}),
             "RmtMode": types.SimpleNamespace(MOVE="move", RCLONE="rclone", MINIO="minio")}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), "exec"), scope)
    return scope["transfer"]


class DownloaderRetryTest(unittest.TestCase):
    def test_failed_transfer_is_not_marked_and_success_is_marked(self):
        transfer = load_transfer()
        client = Mock()
        client.get_transfer_task.return_value = [{"id": "test", "path": "/test/movie.mkv"}]
        app = types.SimpleNamespace(_monitor_downloader_ids=["1"], _DownloaderEnum={"1": "manual"},
                                    get_downloader_conf=Mock(return_value={"name": "test", "rmt_mode": "link"}),
                                    filetransfer=types.SimpleNamespace(transfer_media=Mock()))
        setattr(app, "__get_client", Mock(return_value=client))
        app.filetransfer.transfer_media.return_value = (False, "TMDB unavailable")
        transfer(app)
        client.set_torrents_status.assert_not_called()
        app.filetransfer.transfer_media.return_value = (True, "")
        transfer(app)
        client.set_torrents_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()
