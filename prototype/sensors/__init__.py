# sensors パッケージ
# TOFセンサー（距離センサー）の実装モジュール

# TOFSensorとTOFReadingsは条件付きインポート（ハードウェアモジュールが必要）
try:
    from .tof import TOFSensor, TOFReadings
    __all__ = [
        "TOFSensor",
        "TOFReadings",
    ]
except ImportError:
    # ハードウェアモジュールが利用できない場合
    __all__ = []
