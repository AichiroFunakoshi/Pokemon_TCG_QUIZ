#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pokemon Card Image Mapper
JSONファイルと画像を紐づけて all_cards_local.json を生成

使い方:
    python3 src/image_mapper.py
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import sys

# 設定ファイルをインポート
from config import (
    PROJECT_ROOT, CARD_DATA_DIR, CARD_DETAILS_DIR, LOG_DIR
)

def setup_logging():
    """ロギング設定"""
    log_dir = LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'image_mapper_{timestamp}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)

logger = setup_logging()


def map_images_to_json():
    """card_detailsフォルダ内のJSONと画像を紐づけ"""

    logger.info("=" * 80)
    logger.info("Pokemon Card Image Mapper - Start")
    logger.info(f"Start time: {datetime.now().isoformat()}")
    logger.info("=" * 80)

    if not CARD_DETAILS_DIR.exists():
        logger.error(f"Card details directory not found: {CARD_DETAILS_DIR}")
        return

    all_cards = []
    success_count = 0
    error_count = 0

    # card_detailsフォルダ内の全サブフォルダを走査
    card_folders = sorted([d for d in CARD_DETAILS_DIR.iterdir() if d.is_dir()])

    logger.info(f"Found {len(card_folders)} card folders")

    for card_folder in card_folders:
        try:
            # details.jsonを読み込み
            json_file = card_folder / 'details.json'

            if not json_file.exists():
                logger.warning(f"JSON not found: {card_folder.name}")
                error_count += 1
                continue

            with open(json_file, 'r', encoding='utf-8') as f:
                card_data = json.load(f)

            # 画像パスを確認・追加
            image_file = card_folder / 'image.jpg'

            if image_file.exists():
                # 相対パスに変換
                relative_path = image_file.relative_to(PROJECT_ROOT)
                card_data['image_path'] = str(relative_path)
            else:
                logger.warning(f"Image not found: {card_folder.name}")
                card_data['image_path'] = None

            all_cards.append(card_data)
            success_count += 1

            if success_count % 100 == 0:
                logger.info(f"Processed {success_count} cards...")

        except Exception as e:
            logger.error(f"Error processing {card_folder.name}: {str(e)}")
            error_count += 1

    # all_cards_local.jsonを生成
    output_file = CARD_DATA_DIR / 'all_cards_local.json'

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_cards, f, ensure_ascii=False, indent=2)

        logger.info("=" * 80)
        logger.info(f"✅ Successfully created: {output_file}")
        logger.info(f"Total cards: {len(all_cards)}")
        logger.info(f"Success: {success_count}, Errors: {error_count}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Failed to write output file: {str(e)}")


def main():
    """メイン処理"""
    try:
        map_images_to_json()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info(f"End time: {datetime.now().isoformat()}")


if __name__ == '__main__':
    main()
