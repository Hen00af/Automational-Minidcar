# sensors パッケージ
# TOFセンサー（距離センサー）の実装モジュール

from ..mock.sensors import MockTOFSensor

# TOFSensorとTOFReadingsは条件付きインポート（ハードウェアモジュールが必要）
try:
    from .tof import TOFSensor, TOFReadings
    __all__ = [
        "TOFSensor",
        "TOFReadings",
        "MockTOFSensor",
    ]
except ImportError:
    # ハードウェアモジュールが利用できない場合（モック環境など）
    __all__ = [
        "MockTOFSensor",
    ]
