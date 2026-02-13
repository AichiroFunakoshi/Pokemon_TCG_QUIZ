#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PWA Icon Generator
PWA用のアイコン画像を生成

使い方:
    pip install Pillow
    python3 scripts/generate_icons.py
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# アイコンサイズ
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# 色設定
BACKGROUND_COLOR = (102, 126, 234)  # #667eea
TEXT_COLOR = (255, 255, 255)  # 白

# 出力ディレクトリ
ICONS_DIR = Path(__file__).parent.parent / 'app' / 'icons'


def create_icon(size: int, output_path: Path):
    """アイコン画像を生成"""

    # 画像を作成
    img = Image.new('RGB', (size, size), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # 絵文字（ポケモンカード風）を描画
    # シンプルな図形で表現

    # 外枠（カード型）
    margin = size // 10
    card_rect = [margin, margin, size - margin, size - margin]
    draw.rounded_rectangle(card_rect, radius=size // 20, fill=(255, 255, 255), width=3)

    # 中央に円（モンスターボール風）
    center = size // 2
    circle_radius = size // 4
    circle_bbox = [
        center - circle_radius,
        center - circle_radius,
        center + circle_radius,
        center + circle_radius
    ]
    draw.ellipse(circle_bbox, fill=(220, 53, 69))  # 赤

    # 中央ライン
    line_y = center
    draw.line([(margin, line_y), (size - margin, line_y)], fill=(50, 50, 50), width=max(2, size // 100))

    # 中央の白い円
    small_circle_radius = size // 12
    small_circle_bbox = [
        center - small_circle_radius,
        center - small_circle_radius,
        center + small_circle_radius,
        center + small_circle_radius
    ]
    draw.ellipse(small_circle_bbox, fill=(255, 255, 255), outline=(50, 50, 50), width=max(1, size // 150))

    # 保存
    img.save(output_path, 'PNG')
    print(f"✓ Created: {output_path.name}")


def main():
    """メイン処理"""
    print("=" * 60)
    print("PWA Icon Generator")
    print("=" * 60)

    # ディレクトリ作成
    ICONS_DIR.mkdir(parents=True, exist_ok=True)

    # 各サイズのアイコンを生成
    for size in ICON_SIZES:
        output_path = ICONS_DIR / f'icon-{size}x{size}.png'
        create_icon(size, output_path)

    print("=" * 60)
    print(f"✅ Generated {len(ICON_SIZES)} icons successfully!")
    print(f"Output directory: {ICONS_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
