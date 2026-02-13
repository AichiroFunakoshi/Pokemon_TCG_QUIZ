#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pokemon Card Scraper v35 - Retry Specific Cards
失敗した3枚のみをリトライ：049712, 049713, 049978

修正点：
- エネルギー判定：「特殊エネルギー」を含める
- ポケモンのどうぐ：「AND ワザ」条件を削除
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.pokemon-card.com/card-search/details.php/card"
RETRY_CARD_IDS = [49712, 49713, 49978]  # 失敗した3枚のみ
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_DELAY = 2

ENERGY_TYPE_MAP = {
    'icon-grass': 'grass', 'icon-fire': 'fire', 'icon-water': 'water',
    'icon-lightning': 'lightning', 'icon-psychic': 'psychic',
    'icon-fighting': 'fighting', 'icon-darkness': 'darkness',
    'icon-metal': 'metal', 'icon-colorless': 'colorless',
    'icon-dragon': 'dragon', 'icon-none': 'colorless',
}

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CARD_DETAILS_DIR = PROJECT_ROOT / 'card_data' / 'card_details'
LOG_DIR = SCRIPT_DIR / 'logs'

def setup_logging():
    log_dir = LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'scraper_v35_retry_{timestamp}.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def fetch_with_retry(url: str, card_id: str) -> Optional[str]:
    """リトライ機構付きHTTPリクエスト"""
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Fetching {card_id} (attempt {attempt+1}/{MAX_RETRIES})")
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            logger.info(f"✓ Successfully fetched {card_id}")
            return response.text
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed for {card_id}: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

    logger.error(f"Failed to fetch {card_id} after {MAX_RETRIES} attempts")
    return None

def sanitize_filename(filename: str) -> str:
    """ファイル名から不正な文字を除去（セキュリティ対策）"""
    import re
    # ファイル名に使えない文字を削除: < > : " / \ | ? *
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 先頭・末尾の空白やピリオドを削除
    sanitized = sanitized.strip('. ')
    # 空の場合はデフォルト値
    return sanitized if sanitized else 'unnamed'

# ================================================================================
# v35改善版：カード種判定ロジック
# ================================================================================

def detect_card_type(soup) -> str:
    """v35改善版：カード種判定"""

    # 1. ポケモンカード判定：HP表示がある
    if soup.find('span', class_='hp-num'):
        return 'pokemon'

    # 2. h2タグのテキストで種別判定
    h2_elements = soup.find_all('h2')
    h2_texts = [h2.get_text().strip() for h2 in h2_elements]

    # ポケモンのどうぐ判定：「ポケモンのどうぐ」h2がある（ワザ条件なし）
    if 'ポケモンのどうぐ' in h2_texts:
        return 'pokemon_tool'

    # スタジアム判定：「スタジアム」h2がある
    if 'スタジアム' in h2_texts:
        return 'stadium'

    # グッズ判定：「グッズ」h2がある
    if 'グッズ' in h2_texts:
        return 'goods'

    # サポーター判定：「サポート」h2がある
    if 'サポート' in h2_texts:
        return 'supporter'

    # エネルギー判定：「エネルギー」または「特殊エネルギー」h2がある（v35改善）
    if any('エネルギー' in text for text in h2_texts):
        return 'energy'

    return 'unknown'

# ================================================================================
# ユーティリティ
# ================================================================================

def extract_energy_icons(element) -> Dict[str, int]:
    energy_cost = {}
    if not element:
        return energy_cost
    spans = element.find_all('span', class_='icon')
    for span in spans:
        classes = span.get('class', [])
        for cls in classes:
            if cls in ENERGY_TYPE_MAP:
                energy_type = ENERGY_TYPE_MAP[cls]
                energy_cost[energy_type] = energy_cost.get(energy_type, 0) + 1
                break
    return energy_cost

def extract_description_icons(element) -> List[str]:
    icon_refs = []
    if not element:
        return icon_refs
    spans = element.find_all('span', class_='icon')
    for span in spans:
        classes = span.get('class', [])
        for cls in classes:
            if cls in ENERGY_TYPE_MAP:
                icon_refs.append(ENERGY_TYPE_MAP[cls])
                break
    return icon_refs

# ================================================================================
# パース関数
# ================================================================================

def parse_pokemon_tool(html_content: str, card_id: str) -> Optional[Dict[str, Any]]:
    """ポケモンのどうぐ（v35：ワザ情報あり/なし両対応）"""
    soup = BeautifulSoup(html_content, 'html.parser')
    card_data = {
        'id': card_id, 'name': None, 'card_type': 'pokemon_tool',
        'description': None, 'moves': [],
        'illustrator': None, 'card_number': None, 'card_total': None,
        'set': {}, 'rarity': None, 'image_url': None, 'image_path': None
    }

    try:
        h1 = soup.find('h1', class_='Heading1')
        if h1:
            card_data['name'] = h1.get_text(strip=True)

        right_box = soup.find('div', class_='RightBox-inner')
        if right_box:
            p_elements = right_box.find_all('p')
            if p_elements:
                card_data['description'] = p_elements[0].get_text(strip=True)

            # ワザ情報がある場合のみパース
            h2_elements = right_box.find_all('h2')
            for h2 in h2_elements:
                if 'ワザ' in h2.get_text():
                    h4 = h2.find_next('h4')
                    while h4:
                        move_name_text = ''.join([str(t) for t in h4.contents if isinstance(t, str)]).strip()
                        if not move_name_text:
                            h4 = h4.find_next('h4')
                            if h4 and h4.find_previous('h2') != h2:
                                break
                            continue

                        energy_cost = extract_energy_icons(h4)
                        damage = None
                        damage_span = h4.find('span', class_='f_right')
                        if damage_span:
                            try:
                                damage = int(damage_span.get_text(strip=True))
                            except ValueError:
                                pass

                        description_p = h4.find_next('p')
                        description_text = description_p.get_text(strip=True) if description_p else ""
                        description_icons = extract_description_icons(description_p)

                        card_data['moves'].append({
                            'name': move_name_text, 'energy_cost': energy_cost,
                            'damage': damage, 'description': description_text,
                            'description_icons': description_icons
                        })

                        h4 = h4.find_next('h4')
                        if h4 and h4.find_previous('h2') != h2:
                            break

        author_section = soup.find('div', class_='author')
        if author_section:
            author_link = author_section.find('a')
            if author_link:
                card_data['illustrator'] = author_link.get_text(strip=True)

        subtext = soup.find('div', class_='subtext')
        if subtext:
            text = subtext.get_text(strip=True)
            if '/' in text:
                parts = text.split('/')
                card_data['card_number'] = parts[0].strip()
                try:
                    card_data['card_total'] = int(parts[1].strip())
                except ValueError:
                    card_data['card_total'] = None

        img_tag = soup.find('img', class_='fit')
        if img_tag:
            card_data['image_url'] = img_tag.get('src', '')

        return card_data
    except Exception as e:
        logger.error(f"Error parsing pokemon tool {card_id}: {str(e)}")
        return None

def parse_energy_card(html_content: str, card_id: str) -> Optional[Dict[str, Any]]:
    """エネルギーカード（新規パース関数）"""
    soup = BeautifulSoup(html_content, 'html.parser')
    card_data = {
        'id': card_id, 'name': None, 'card_type': 'energy',
        'energy_type': None, 'description': None,
        'illustrator': None, 'card_number': None, 'card_total': None,
        'set': {}, 'rarity': None, 'image_url': None, 'image_path': None
    }

    try:
        h1 = soup.find('h1', class_='Heading1')
        if h1:
            card_data['name'] = h1.get_text(strip=True)

        right_box = soup.find('div', class_='RightBox-inner')
        if right_box:
            # エネルギータイプをiconから抽出
            h2_elements = right_box.find_all('h2')
            for h2 in h2_elements:
                if 'エネルギー' in h2.get_text():
                    # h2の直後のpで説明文を取得
                    p = h2.find_next('p')
                    if p:
                        card_data['description'] = p.get_text(strip=True)
                        # iconからエネルギータイプを抽出
                        energy_icons = extract_energy_icons(p)
                        if energy_icons:
                            card_data['energy_type'] = list(energy_icons.keys())[0]

        author_section = soup.find('div', class_='author')
        if author_section:
            author_link = author_section.find('a')
            if author_link:
                card_data['illustrator'] = author_link.get_text(strip=True)

        subtext = soup.find('div', class_='subtext')
        if subtext:
            text = subtext.get_text(strip=True)
            if '/' in text:
                parts = text.split('/')
                card_data['card_number'] = parts[0].strip()
                try:
                    card_data['card_total'] = int(parts[1].strip())
                except ValueError:
                    card_data['card_total'] = None

        img_tag = soup.find('img', class_='fit')
        if img_tag:
            card_data['image_url'] = img_tag.get('src', '')

        return card_data
    except Exception as e:
        logger.error(f"Error parsing energy card {card_id}: {str(e)}")
        return None

# ================================================================================
# リトライ実行
# ================================================================================

def retry_failed_cards():
    """失敗した3枚のみをリトライ"""
    success_count = 0
    error_count = 0

    logger.info("=" * 80)
    logger.info("Pokemon Card Scraper v35 - Retry 3 Failed Cards")
    logger.info(f"Target cards: {RETRY_CARD_IDS}")
    logger.info("=" * 80)

    for card_id_int in RETRY_CARD_IDS:
        card_id = str(card_id_int).zfill(6)

        try:
            url = f"{BASE_URL}/{card_id}/regu/XY"
            html_content = fetch_with_retry(url, card_id)

            if not html_content:
                error_count += 1
                continue

            soup = BeautifulSoup(html_content, 'html.parser')
            card_type = detect_card_type(soup)

            logger.info(f"Card {card_id}: Detected type = {card_type}")

            if card_type == 'pokemon_tool':
                card_data = parse_pokemon_tool(html_content, card_id)
            elif card_type == 'energy':
                card_data = parse_energy_card(html_content, card_id)
            else:
                logger.warning(f"Unexpected type for {card_id}: {card_type}")
                error_count += 1
                continue

            if not card_data or not card_data.get('name'):
                error_count += 1
                continue

            # フォルダとJSONを保存（ファイル名をサニタイズ）
            safe_card_name = sanitize_filename(card_data['name'])
            card_folder = CARD_DETAILS_DIR / f"{card_id}_{safe_card_name}"
            card_folder.mkdir(parents=True, exist_ok=True)

            json_file = card_folder / 'details.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(card_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ Saved {card_id} ({card_data['name']}) as {card_type}")
            success_count += 1

            time.sleep(0.5)

        except Exception as e:
            error_count += 1
            logger.error(f"Error processing {card_id}: {str(e)}")

    logger.info("=" * 80)
    logger.info(f"✅ Retry completed!")
    logger.info(f"Success: {success_count}, Errors: {error_count}")
    logger.info("=" * 80)

def main():
    logger.info("=" * 80)
    logger.info("Pokemon Card Scraper v35 - Retry Failed Cards Only")
    logger.info(f"Start time: {datetime.now().isoformat()}")
    logger.info("=" * 80)

    try:
        retry_failed_cards()
    except Exception as e:
        logger.error(f"Failed: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("=" * 80)
        logger.info(f"End time: {datetime.now().isoformat()}")
        logger.info("=" * 80)

if __name__ == '__main__':
    main()
