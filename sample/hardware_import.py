"""
ハードウェアモジュールの自動インポート
Raspberry Pi環境では実機モジュールを、それ以外ではモックを使用
"""
import sys
import os

def is_raspberry_pi():
    """Raspberry Pi環境かどうかを判定"""
    # /proc/cpuinfo に Raspberry Pi の情報があるか確認
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            return 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
    except (FileNotFoundError, PermissionError):
        pass
    
    # 環境変数で強制的にモックを使用する場合
    if os.environ.get('USE_MOCK_HARDWARE', '').lower() in ('1', 'true', 'yes'):
        return False
    
    return False  # Docker環境では常にFalse

# Raspberry Pi環境かどうかを判定
_use_mock = not is_raspberry_pi()

if _use_mock:
    print("[INFO] Hardware modules not available, using mock:", file=sys.stderr)
    print("[INFO] Using mock hardware modules (board_mock, busio_mock, digitalio_mock, pca9685_mock)", file=sys.stderr)
    
    # モックモジュールをインポート
    import board_mock as board
    import busio_mock as busio
    import digitalio_mock as digitalio
    import pca9685_mock
    
    # グローバル名前空間に追加
    sys.modules['board'] = board
    sys.modules['busio'] = busio
    sys.modules['digitalio'] = digitalio
    # adafruit_pca9685 をインポートする前にモックを登録
    sys.modules['adafruit_pca9685'] = pca9685_mock
else:
    # 実機モジュールをインポート
    import board
    import busio
    import digitalio

# エクスポート（digitalio も含める）
__all__ = ['board', 'busio', 'digitalio', 'is_raspberry_pi']

# グローバル名前空間に直接追加（from hardware_import import board, busio で使用可能）
if _use_mock:
    # モックモジュールを直接エクスポート
    pass  # 既に sys.modules に登録済み
else:
    # 実機モジュールを直接エクスポート
    pass  # 既にインポート済み
