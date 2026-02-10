#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pokemon Card Scraper - Main Scraping Script
XYレギュレーション全カードをスクレイピング

使い方:
    python3 src/scraper.py

特徴:
- 進捗保存（中断後も続きから再開可能）
- 既存カード自動スキップ
- エラーハンドリング完備
- 画像自動ダウンロード
"""

import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from bs4 import BeautifulSoup

# 設定ファイルをインポート
from config import (
    BASE_URL, REGULATION, CARD_ID_START, CARD_ID_END,
    DELAY_PER_CARD, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY,
    CARD_DETAILS_DIR, DATA_DIR, LOG_DIR, PROGRESS_FILE,
    ENERGY_TYPE_MAP, PROGRESS_INTERVAL, PROJECT_ROOT
)


def setup_logging():
    """ロギング設定"""
    log_dir = LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'scraper_{timestamp}.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)


# ロガーはmain()で初期化
logger = None


def fetch_with_retry(url: str, card_id: str) -> Optional[str]:
    """リトライ機構付きHTTPリクエスト"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed for {card_id}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

    logger.error(f"Failed to fetch {card_id} after {MAX_RETRIES} attempts")
    return None


def sanitize_filename(filename: str) -> str:
    """ファイル名から不正な文字を除去（セキュリティ対策）"""
    # ファイル名に使えない文字を削除: < > : " / \ | ? *
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 先頭・末尾の空白やピリオドを削除
    sanitized = sanitized.strip('. ')
    # 空の場合はデフォルト値
    return sanitized if sanitized else 'unnamed'


def download_image(image_url: str, save_path: Path) -> bool:
    """画像をダウンロード"""
    try:
        response = requests.get(image_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            f.write(response.content)

        return True
    except Exception as e:
        logger.error(f"Failed to download image: {str(e)}")
        return False


def parse_card_html(html_content: str, card_id: str) -> Optional[Dict[str, Any]]:
    """HTMLをパースしてカード情報を抽出（簡易版）"""
    soup = BeautifulSoup(html_content, 'html.parser')

    card_data = {
        'id': card_id,
        'name': None,
        'card_type': 'unknown',
        'hp': None,
        'type': None,
        'stage': None,
        'abilities': [],
        'moves': [],
        'description': None,
        'weakness': None,
        'resistance': None,
        'illustrator': None,
        'card_number': None,
        'image_url': None,
        'image_path': None
    }

    try:
        # カード名
        h1 = soup.find('h1', class_='Heading1')
        if h1:
            card_data['name'] = h1.get_text(strip=True)

        # HP
        hp_span = soup.find('span', class_='hp-num')
        if hp_span:
            try:
                card_data['hp'] = int(hp_span.get_text(strip=True))
            except ValueError:
                pass

        # イラストレーター
        author_section = soup.find('div', class_='author')
        if author_section:
            author_link = author_section.find('a')
            if author_link:
                card_data['illustrator'] = author_link.get_text(strip=True)

        # カード番号
        subtext = soup.find('div', class_='subtext')
        if subtext:
            text = subtext.get_text(strip=True)
            if '/' in text:
                parts = text.split('/')
                card_data['card_number'] = parts[0].strip()

        # 画像URL
        img_tag = soup.find('img', class_='fit')
        if img_tag:
            card_data['image_url'] = img_tag.get('src', '')

        return card_data

    except Exception as e:
        logger.error(f"Error parsing card {card_id}: {str(e)}")
        return None


def load_progress() -> Dict[str, Any]:
    """進捗データを読み込み（パフォーマンス最適化：setに変換）"""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # リストをsetに変換（O(1)検索のため）
                data['completed_cards'] = set(data.get('completed_cards', []))
                data['failed_cards'] = set(data.get('failed_cards', []))
                return data
        except Exception as e:
            logger.warning(f"Failed to load progress: {str(e)}")

    return {
        'last_card_id': CARD_ID_START - 1,
        'completed_cards': set(),
        'failed_cards': set()
    }


def save_progress(progress: Dict[str, Any]):
    """進捗データを保存（setをlistに変換）"""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        # setをlistに変換してJSON保存
        progress_copy = progress.copy()
        progress_copy['completed_cards'] = list(progress['completed_cards'])
        progress_copy['failed_cards'] = list(progress['failed_cards'])
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress_copy, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save progress: {str(e)}")


def scrape_all_cards():
    """全カードをスクレイピング"""
    logger.info("=" * 80)
    logger.info("Pokemon Card Scraper - Start")
    logger.info(f"Card ID Range: {CARD_ID_START} - {CARD_ID_END}")
    logger.info("=" * 80)

    progress = load_progress()
    success_count = 0
    skip_count = 0
    error_count = 0

    try:
        for card_id_int in range(CARD_ID_START, CARD_ID_END + 1):
            card_id = str(card_id_int).zfill(6)

            # 既にスクレイピング済みの場合はスキップ
            if card_id in progress['completed_cards']:
                skip_count += 1
                continue

            try:
                url = f"{BASE_URL}/{card_id}/regu/{REGULATION}"
                html_content = fetch_with_retry(url, card_id)

                if not html_content:
                    progress['failed_cards'].add(card_id)
                    error_count += 1
                    continue

                card_data = parse_card_html(html_content, card_id)

                if not card_data or not card_data.get('name'):
                    progress['failed_cards'].add(card_id)
                    error_count += 1
                    continue

                # カードフォルダを作成（ファイル名をサニタイズ）
                safe_card_name = sanitize_filename(card_data['name'])
                card_folder = CARD_DETAILS_DIR / f"{card_id}_{safe_card_name}"
                card_folder.mkdir(parents=True, exist_ok=True)

                # 画像をダウンロード（ダウンロード失敗時はスキップ）
                image_downloaded = False
                if card_data['image_url']:
                    image_path = card_folder / 'image.jpg'
                    image_downloaded = download_image(card_data['image_url'], image_path)
                    if image_downloaded:
                        # 相対パスを設定（ValueError対策）
                        try:
                            card_data['image_path'] = str(image_path.relative_to(PROJECT_ROOT))
                        except ValueError:
                            # CARD_DETAILS_DIRがPROJECT_ROOT外の場合は絶対パス
                            logger.warning(f"Cannot compute relative path for {card_id}, using absolute path")
                            card_data['image_path'] = str(image_path)
                    else:
                        logger.warning(f"Failed to download image for {card_id}")
                        card_data['image_path'] = None

                # JSONを保存
                json_file = card_folder / 'details.json'
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(card_data, f, ensure_ascii=False, indent=2)

                progress['completed_cards'].add(card_id)
                progress['last_card_id'] = card_id_int
                success_count += 1

                logger.info(f"✓ Scraped {card_id}: {card_data['name']} (image: {'OK' if image_downloaded else 'FAILED'})")

                # 定期的に進捗を保存
                if success_count % PROGRESS_INTERVAL == 0:
                    save_progress(progress)
                    logger.info(f"Progress: {success_count} cards completed")

                time.sleep(DELAY_PER_CARD)

            except Exception as e:
                logger.error(f"Error processing {card_id}: {str(e)}")
                progress['failed_cards'].add(card_id)
                error_count += 1

    finally:
        # 中断時も必ず進捗を保存
        save_progress(progress)

    logger.info("=" * 80)
    logger.info("✅ Scraping completed!")
    logger.info(f"Success: {success_count}, Skipped: {skip_count}, Errors: {error_count}")
    logger.info("=" * 80)


def main():
    """メイン処理"""
    global logger
    logger = setup_logging()

    try:
        scrape_all_cards()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info(f"End time: {datetime.now().isoformat()}")


if __name__ == '__main__':
    main()
