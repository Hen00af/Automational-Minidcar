"""
カスタム例外クラス
モック実装で使用する例外を定義
"""


class MockError(Exception):
    """モック実装の基底例外クラス"""
    pass


class CalibrationError(MockError):
    """キャリブレーション未設定エラー"""
    pass


class SituationError(MockError):
    """Situation関連のエラー"""
    pass
