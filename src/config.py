#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pokemon Card Scraper - Configuration File
共通設定ファイル

このファイルでスクレイピングの動作をカスタマイズできます。
"""

from pathlib import Path

# ================================================================================
# プロジェクトパス設定
# ================================================================================

# プロジェクトのルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent

# データディレクトリ
CARD_DATA_DIR = PROJECT_ROOT / 'card_data'
CARD_DETAILS_DIR = CARD_DATA_DIR / 'card_details'
CARD_IMAGES_DIR = CARD_DATA_DIR / 'images'

# 進捗管理ディレクトリ
DATA_DIR = PROJECT_ROOT / 'data'
PROGRESS_FILE = DATA_DIR / 'progress.json'
SCRAPED_IDS_FILE = DATA_DIR / 'scraped_ids.json'

# ログディレクトリ
LOG_DIR = PROJECT_ROOT / 'logs'

# ================================================================================
# スクレイピング設定
# ================================================================================

# ベースURL
BASE_URL = "https://www.pokemon-card.com/card-search/details.php/card"
REGULATION = "XY"  # XYレギュレーション

# ページ数制限（全150ページ）
PAGE_LIMIT = 150

# カードID範囲
CARD_ID_START = 49634
CARD_ID_END = 50012

# ================================================================================
# タイミング設定
# ================================================================================

# リクエスト間隔（秒）
DELAY_PER_PAGE = 0.5      # ページ間の待機時間
DELAY_PER_CARD = 0.3      # カード間の待機時間

# タイムアウト設定
REQUEST_TIMEOUT = 15      # HTTPリクエストタイムアウト（秒）

# リトライ設定
MAX_RETRIES = 3          # 最大リトライ回数
RETRY_DELAY = 2          # リトライ間隔（秒）

# ================================================================================
# タイプアイコン設定（絵文字）
# ================================================================================

TYPE_EMOJIS = {
    'normal': '⚪',      # ノーマル
    'fire': '🔥',       # ほのお
    'water': '💧',      # みず
    'lightning': '⚡',   # でんき
    'grass': '🌿',      # くさ
    'ice': '❄️',        # こおり
    'fighting': '👊',   # かくとう
    'poison': '☠️',     # どく
    'ground': '⛰️',     # じめん
    'flying': '🦅',     # ひこう
    'psychic': '👁️',    # エスパー
    'bug': '🐛',        # むし
    'rock': '🪨',       # いわ
    'ghost': '👻',      # ゴースト
    'dragon': '🐉',     # ドラゴン
    'darkness': '👿',   # あく
    'dark': '👿',       # あく（別名）
    'metal': '⚙️',      # はがね
    'fairy': '🧚',      # フェアリー
    'colorless': '⚪',  # むしょく
}

# HTMLクラス名とタイプのマッピング
ENERGY_TYPE_MAP = {
    'icon-grass': 'grass',
    'icon-fire': 'fire',
    'icon-water': 'water',
    'icon-lightning': 'lightning',
    'icon-psychic': 'psychic',
    'icon-fighting': 'fighting',
    'icon-darkness': 'darkness',
    'icon-dark': 'darkness',
    'icon-metal': 'metal',
    'icon-colorless': 'colorless',
    'icon-dragon': 'dragon',
    'icon-none': 'colorless',
}

# ================================================================================
# ログ設定
# ================================================================================

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ================================================================================
# その他設定
# ================================================================================

# バックアップ設定
ENABLE_BACKUP = True       # バックアップを有効化
BACKUP_DIR = PROJECT_ROOT / 'scrapers' / 'backups'

# 進捗表示間隔
PROGRESS_INTERVAL = 50     # 50枚ごとに進捗を表示


def ensure_directories():
    """必要なディレクトリを作成"""
    directories = [
        CARD_DATA_DIR,
        CARD_DETAILS_DIR,
        CARD_IMAGES_DIR,
        DATA_DIR,
        LOG_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    # 設定確認用
    print("=" * 80)
    print("Pokemon Card Scraper - Configuration")
    print("=" * 80)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Card Data Dir: {CARD_DATA_DIR}")
    print(f"Log Dir: {LOG_DIR}")
    print(f"Base URL: {BASE_URL}")
    print(f"Page Limit: {PAGE_LIMIT}")
    print(f"Card ID Range: {CARD_ID_START} - {CARD_ID_END}")
    print("=" * 80)

    ensure_directories()
    print("✓ All directories created successfully")
