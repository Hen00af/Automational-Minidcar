import schemdraw
import schemdraw.elements as elm

# 回路図の設定
with schemdraw.Drawing() as d:
    d.config(fontsize=12, unit=3)

    # --- 1. Raspberry Pi (左側) ---
    # ラズパイをブラックボックスとして定義
    rpi = elm.Ic(pins=[
        elm.IcPin(name='3.3V', side='right', slot='1/4'),
        elm.IcPin(name='SDA', side='right', slot='2/4'),
        elm.IcPin(name='SCL', side='right', slot='3/4'),
        elm.IcPin(name='GND', side='right', slot='4/4'),
    ], w=3, h=6)
    d += rpi
    # 部品名を図の下に配置（現在位置の下）
    rpi_label_pos = d.here
    d.move(dy=-1.5)
    d += elm.Label().label('Raspberry Pi 4', loc='center', fontsize=12)
    d.here = rpi_label_pos

    # --- 2. PCA9685 (中央) ---
    d.move(dx=6)
    pca = elm.Ic(pins=[
        elm.IcPin(name='VCC', side='left', slot='1/4'),
        elm.IcPin(name='SDA', side='left', slot='2/4'),
        elm.IcPin(name='SCL', side='left', slot='3/4'),
        elm.IcPin(name='GND', side='left', slot='4/4'),
        # Outputs
        elm.IcPin(name='PWM0', side='right', slot='1/3'),
        elm.IcPin(name='PWM1', side='right', slot='2/3'),
        elm.IcPin(name='PWM2', side='right', slot='3/3'),
    ], w=4, h=6)
    d += pca
    # 部品名を図の下に配置（現在位置の下）
    pca_label_pos = d.here
    d.move(dy=-1.5)
    d += elm.Label().label('PCA9685', loc='center', fontsize=12)
    d.here = pca_label_pos

    # --- RPi <-> PCA 接続 ---
    # ピン名で識別できるため、接続線のラベルは省略（文字の重なりを防止）
    d += elm.Line().at(getattr(rpi, 'SDA')).to(getattr(pca, 'SDA'))
    d += elm.Line().at(getattr(rpi, 'SCL')).to(getattr(pca, 'SCL'))
    d += elm.Line().at(getattr(rpi, '3.3V')).to(getattr(pca, 'VCC'))
    d += elm.Line().at(getattr(rpi, 'GND')).to(getattr(pca, 'GND'))

    # --- 3. Servo (右上) ---
    d.move(dx=5, dy=3)
    servo = elm.Motor().label('Steering\nServo', loc='bottom', fontsize=10)
    # PWM0はピン名で識別できるため、ラベルは省略
    d += elm.Wire('|-').at(getattr(pca, 'PWM0')).to(servo.start)
    
    # --- 4. Motor Driver (右下) ---
    d.move(dx=0, dy=-6)
    driver = elm.Ic(pins=[
        elm.IcPin(name='IN1', side='left', slot='1/2'),
        elm.IcPin(name='IN2', side='left', slot='2/2'),
        elm.IcPin(name='OUT1', side='right', slot='1/2'),
        elm.IcPin(name='OUT2', side='right', slot='2/2'),
    ], w=3, h=4)
    d += driver
    # 部品名を図の下に配置（現在位置の下）
    driver_label_pos = d.here
    d.move(dy=-1.2)
    d += elm.Label().label('L298N Driver', loc='center', fontsize=12)
    d.here = driver_label_pos

    # --- PCA <-> Driver 接続 ---
    # ピン名で識別できるため、接続線のラベルは省略（文字の重なりを防止）
    d += elm.Wire('|-').at(getattr(pca, 'PWM1')).to(getattr(driver, 'IN1'))
    d += elm.Wire('|-').at(getattr(pca, 'PWM2')).to(getattr(driver, 'IN2'))

    # --- 5. DC Motor ---
    d.move(dx=4)
    motor = elm.Motor().label('DC Motor', loc='bottom', fontsize=10)
    d += elm.Wire().at(getattr(driver, 'OUT1')).to(motor.start)
    d += elm.Wire().at(getattr(driver, 'OUT2')).to(motor.end)

    # 保存（SVG形式 - ベクター形式で高品質）
    d.save('circuit_diagram.svg')
    print("✅ 回路図を 'circuit_diagram.svg' に保存しました。")
    print("   ブラウザで開いて確認できます。")