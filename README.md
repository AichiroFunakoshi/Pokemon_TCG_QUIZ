# ポケモンカード検索アプリ / Pokemon Card Search App

ポケモンカードゲームのカード情報を検索できるWebアプリケーションです。
1,283枚のカード情報と画像をローカルで検索できます。

**プロジェクトの最終目標**: ポケモンカードゲームに関するクイズを自動的に作成するシステム
**現在のフェーズ**: カード情報スクレイピング＆検索の土台作り

---

## 🎯 機能

- 🔍 **カード検索**: カード名で高速検索
- 🖼️ **画像表示**: 高品質なカード画像を表示
- 📊 **詳細情報**: HP、タイプ、ワザ、効果など全情報を表示
- 🎨 **タイプアイコン**: 18種類のポケモンタイプを絵文字で表示
- ⚡ **高速**: サーバー不要でローカルで動作

---

## 📁 プロジェクト構成

```
Pokemon_TCG_QUIZ/
├── app/                          # 📱 Webアプリケーション
│   └── index.html               # メインページ（ブラウザで開く）
├── src/                         # 🐍 Pythonスクリプト（メイン）
│   ├── __init__.py             # パッケージ定義
│   ├── config.py               # ✅ 共通設定ファイル（重要）
│   ├── scraper.py              # ✅ スクレイピング実行（最終版）
│   └── image_mapper.py         # ✅ JSONと画像を紐づけ
├── card_data/                  # 💾 カードデータ
│   ├── all_cards_local.json   # ローカル版（画像紐付け）
│   ├── card_details/          # 個別カード（JSON+画像）
│   └── images/               # カード画像
├── data/                       # 📊 進捗・状態ファイル
│   ├── progress.json          # スクレイピング進捗
│   └── scraped_ids.json       # スクレイピング済みID
├── logs/                       # 📝 ログファイル
│   ├── scraper_*.log          # スクレイパーログ
│   └── image_mapper_*.log     # マッパーログ
├── scrapers/                   # 🔧 スクレイピングスクリプト
│   └── v35_retry/             # v35リトライ版
├── reference/                  # 📚 参考資料（PDF等）
│   ├── advanced_manual.pdf
│   ├── floor-rule_*.pdf
│   ├── penalty_*.pdf
│   ├── ruling_*.pdf
│   └── 参考問題.rtf
├── deprecated/                 # 🗑️ 古いバージョン
│   └── (古いスクレイパーなど)
└── README.md                   # 📖 このファイル
```

---

## 🚀 クイックスタート

### 1. 簡易HTTPサーバーを起動

```bash
cd Pokemon_TCG_QUIZ
python3 -m http.server 8000
```

### 2. ブラウザで開く

```
http://localhost:8000/app/index.html
```

### 3. カード名を検索

検索ボックスにカード名を入力して検索します。
例：`ピカチュウ`、`オーベム`、`リブートポッド`

### 4. PWAとしてインストール（オプション）

**デスクトップ（Chrome/Edge）**:
1. アドレスバー右側の「インストール」アイコンをクリック
2. 「インストール」ボタンをクリック
3. デスクトップアプリとして起動可能

**モバイル（iOS Safari）**:
1. 共有ボタン（□↑）をタップ
2. 「ホーム画面に追加」を選択
3. ホーム画面のアイコンから起動

**モバイル（Android Chrome）**:
1. メニュー（⋮）を開く
2. 「ホーム画面に追加」を選択
3. ホーム画面のアイコンから起動

**PWAの特徴**:
- ✅ オフラインでも動作（一度読み込めば）
- ✅ ネイティブアプリのように動作
- ✅ 高速なロード時間（キャッシュ活用）
- ✅ インストール不要で使い始められる

---

## 🔧 開発者向け

### スクレイピングスクリプトについて

**最新版スクレイパー**: `src/scraper.py`
- XYレギュレーション全150ページをスクレイピング
- ポケモン・トレーナーズカード両対応
- 自動的に画像をダウンロード
- エラーハンドリング完備

**v35リトライ版**: `scrapers/v35_retry/`
- 失敗したカードのみをリトライ
- エネルギー判定改善（「特殊エネルギー」対応）
- ポケモンのどうぐ判定改善

**古いバージョン**: `deprecated/` フォルダ
- 初期バージョンのスクレイパー群

> 新規スクレイピングは `src/scraper.py` を使用してください。

### スクレイピングを実行する

```bash
# 仮想環境を有効化（推奨）
python3 -m venv venv
source venv/bin/activate

# 必要なパッケージをインストール
pip install requests beautifulsoup4 selenium webdriver-manager

# スクレイピング実行（既存カードはスキップ）
python3 src/scraper.py
```

**進捗について**:
- `data/progress.json` に進捗が保存されます
- 中断後も続きから再開できます
- 既にスクレイピング済みのカードは自動的にスキップされます

### JSONと画像を紐づける

新しくカードを追加した後、以下を実行：

```bash
python3 src/image_mapper.py
```

これにより `card_data/all_cards_local.json` が生成されます。

### 設定を変更する

`src/config.py` で以下をカスタマイズできます：

```python
# ページ数制限
PAGE_LIMIT = 150

# 取得のタイミング間隔
DELAY_PER_PAGE = 0.5      # ページ間の待機時間
DELAY_PER_CARD = 0.3      # カード間の待機時間

# タイプアイコン（絵文字）
TYPE_EMOJIS = {
    'fire': '🔥',      # ここを変更
    # ...
}
```

---

## 📊 データ仕様

### all_cards_local.json の構造

```json
[
  {
    "id": "045350",
    "name": "オーベム",
    "card_number": "009/053",
    "hp": "100",
    "type": "psychic",
    "stage": "1 進化",
    "abilities": [
      {
        "name": "コスモビート",
        "damage": "20×"
      }
    ],
    "description": "効果説明テキスト",
    "weakness": "×2",
    "resistance": "－30",
    "illustrator": "Shinya Komatsu",
    "image_path": "card_data/card_details/045350_オーベム/image.jpg"
  }
]
```

---

## 🎨 タイプアイコン一覧

| タイプ | 絵文字 | 英語名 |
|--------|--------|--------|
| ノーマル | ⚪ | normal |
| ほのお | 🔥 | fire |
| みず | 💧 | water |
| でんき | ⚡ | lightning |
| くさ | 🌿 | grass |
| こおり | ❄️ | ice |
| かくとう | 👊 | fighting |
| どく | ☠️ | poison |
| じめん | ⛰️ | ground |
| ひこう | 🦅 | flying |
| エスパー | 👁️ | psychic |
| むし | 🐛 | bug |
| いわ | 🪨 | rock |
| ゴースト | 👻 | ghost |
| ドラゴン | 🐉 | dragon |
| あく | 👿 | darkness |
| はがね | ⚙️ | metal |
| フェアリー | 🧚 | fairy |

---

## 🔍 スクレイピング詳細（v35版）

### v35 - 完全JSON対応版

**実装日**: 2026-01-29
**対応カード数**: 1,245枚（XYレギュレーション）

#### スクレイピング対象URL

```
https://www.pokemon-card.com/card-search/details.php/card/{card_id}/regu/XY
```

#### 実装された機能

1. **基本情報抽出**
   - カード名、HP、タイプ、進化段階

2. **特性情報（Abilities）**
   - 特性名、説明文、説明文中の参照マーク

3. **技情報（Moves）**
   - 技名、エネルギーコスト（個数）、ダメージ、説明文

4. **弱点・抵抗力・にげるコスト**
   - 弱点タイプと倍率
   - 抵抗力タイプと値
   - にげるコスト（個数）

5. **進化情報**
   - 進化元（from）、進化先（to）

6. **メタデータ**
   - イラストレーター、カード番号、セット、レアリティ

7. **特別なルール**
   - ex/GX/V等の特別ルール

#### JSON出力形式例

```json
{
  "id": "049645",
  "name": "ジュナイパーex",
  "basic_info": {
    "hp": 250,
    "type": "grass",
    "stage": "Stage 2"
  },
  "abilities": [
    {
      "name": "特性名",
      "type": "ability",
      "description": "説明文...",
      "description_icons": ["grass", "colorless"]
    }
  ],
  "moves": [
    {
      "name": "技名",
      "energy_cost": {"grass": 2, "colorless": 1},
      "damage": 100,
      "description": "説明文...",
      "description_icons": ["fire", "water"]
    }
  ],
  "weakness": {
    "type": "fire",
    "multiplier": 2
  },
  "resistance": null,
  "escape_cost": {"colorless": 1},
  "evolution": {
    "from": ["ポケモンA"],
    "to": ["ポケモンB"]
  },
  "illustrator": "イラストレーター名",
  "card_number": "012",
  "card_total": 80,
  "set": {"code": "XY"},
  "rarity": "EX",
  "image_url": "https://...",
  "image_path": "card_data/card_details/049645_ジュナイパーex/image.jpg"
}
```

---

## 🐛 トラブルシューティング

### 画像が表示されない場合

```bash
# image_mapper.py を実行して JSON を再生成
python3 src/image_mapper.py

# ブラウザをリロード
```

### サーバーが起動しない場合

```bash
# ポート 8000 が使用中の可能性
python3 -m http.server 8001  # 別ポートで試す
```

### JSON読み込みエラー

```bash
# all_cards_local.json が存在するか確認
ls -la card_data/all_cards_local.json

# なければ image_mapper.py を実行
python3 src/image_mapper.py
```

### スクレイピングがエラーで止まる場合

```bash
# ブラウザドライバをアップデート
pip install --upgrade webdriver-manager

# 再度実行（進捗から再開）
python3 src/scraper.py
```

---

## 🌐 PWA化・GitHub Pages対応

### ✅ PWA実装済み

このアプリはProgressive Web App (PWA)として実装されています。

**実装内容**:
- ✅ `app/manifest.json` - アプリメタデータ
- ✅ `app/service-worker.js` - オフライン対応とキャッシュ戦略
- ✅ `app/icons/` - 複数サイズのアイコン（72px～512px）
- ✅ Service Worker登録（index.html内）
- ✅ オフラインキャッシュ対応

**PWA機能**:
- 📱 ホーム画面に追加可能（iOS/Android/Desktop）
- 🚀 高速ロード（アプリシェルキャッシュ）
- 📡 オフライン動作（一度読み込めば）
- 🔄 バックグラウンド同期（将来拡張可能）
- 🔔 プッシュ通知（将来拡張可能）

**キャッシュ戦略**:
- **HTMLファイル**: ネットワーク優先 → フォールバックでキャッシュ
- **JSONデータ**: ネットワーク優先 → 成功時にキャッシュ更新
- **画像**: キャッシュ優先 → なければネットワーク取得

### GitHub Pages対応

GitHub Pagesでホスティングする場合：

1. リポジトリの設定で GitHub Pages を有効化
2. ソースを `main` ブランチまたは `gh-pages` ブランチに設定
3. カスタムドメインを設定（オプション）

**注意事項**:
- Service Workerは HTTPS 環境でのみ動作します
- GitHub Pagesは自動的にHTTPSを提供します

---

## 📚 参考資料

`reference/` フォルダに以下の公式資料を保存予定：

- `advanced_manual.pdf` - 高度なルール
- `floor-rule_*.pdf` - フロアルール
- `penalty_*.pdf` - ペナルティガイドライン
- `ruling_*.pdf` - 裁定事例
- `参考問題.rtf` - 参考問題集

---

## 📄 ライセンス

ポケモンカード情報は公式サイト（pokemon-card.com）から取得しています。
利用規約をご確認ください。

---

## 👤 作成者

Tetsuo

---

## 📅 更新履歴

- **2026-02-10**: PWA実装完了（manifest.json、service-worker.js、アイコン生成）
- **2026-02-04**: プロジェクトリポジトリ初期化、ディレクトリ構造構築
- **2026-01-29**: v35スクレイパー実装（エネルギー判定改善）
- **2026-01-27**: スクレイパー統一整理、古いバージョンをdeprecatedフォルダに移動
- **2026-01-27**: プロジェクト構成の大幅整理、image_mapper.py 実装
- **2026-01-26**: 初回スクレイピング完了（1,283枚）

---

## 🚀 今後の展開

1. **フェーズ1（現在）**: カード情報スクレイピング＆検索システム構築 ✅
2. **フェーズ2（次）**: ポケモンカードゲームルールのデータ化
3. **フェーズ3（最終目標）**: クイズ自動生成システムの実装

---

**Status**: 🚧 開発中（フェーズ1）
