# CSV Table Converter

CSV/TSV/PSVファイルを美しいASCII表やマークダウン表に変換するPythonツールです。完全なUnicode対応で、日本語をはじめとする全角文字も正確に表示できます。

## ✨ 主な機能

- **複数の出力形式対応**: ASCII表とマークダウン表の両方に対応
- **完全なUnicode対応**: 日本語・中国語・韓国語などの全角文字を正確に表示
- **智的自動検出**: 区切り文字とヘッダーの自動判定
- **多様なエンコーディング対応**: UTF-8、Shift_JIS、CP932、EUC-JPなど8種類に対応
- **自動保存機能**: ファイル名自動生成による簡単保存
- **全角スペース対応**: 環境依存の表示崩れを解決
- **豊富なオプション**: 列幅制限・カスタム区切り文字など

## 🚀 クイックスタート

```bash
# 基本的な使用 - ASCII表で表示
python table_converter.py data.csv

# 自動保存（data.txt として保存）
python table_converter.py data.csv --save

# マークダウン表を生成
python table_converter.py data.csv --format markdown --save

# 全角スペース問題を解決（日本語データ推奨）
python table_converter.py data.csv --normalize-ws --save
```

## 📋 出力例

### 入力CSV
```csv
Name,Age,City
田中太郎,25,東京
鈴木花子,30,大阪
佐藤次郎,28,福岡
```

### ASCII表出力
```
+----------+------+------+
| Name     | Age  | City |
+----------+------+------+
| 田中太郎 | 25   | 東京 |
| 鈴木花子 | 30   | 大阪 |
| 佐藤次郎 | 28   | 福岡 |
+----------+------+------+
```

### マークダウン表出力
```markdown
| Name     | Age  | City |
|----------|------|------|
| 田中太郎 | 25   | 東京 |
| 鈴木花子 | 30   | 大阪 |
| 佐藤次郎 | 28   | 福岡 |
```

## 📖 使用方法

```bash
python table_converter.py [オプション] 入力ファイル
```

### コマンドラインオプション

| オプション | 説明 |
|-----------|------|
| `-o, --output ファイル名` | 出力ファイル名を指定 |
| `--save` | 自動ファイル名生成で保存 |
| `--format {ascii,markdown}` | 出力形式選択（デフォルト: ascii） |
| `--normalize-ws` | 全角スペースを正規化して安定表示 |
| `--max-width N` | 列幅をN文字に制限 |
| `--no-align` | マークダウン最小形式（列揃えなし） |
| `--header` | 強制的にヘッダーありとして処理 |
| `--no-header` | 強制的にヘッダーなしとして処理 |
| `-d 文字` | 区切り文字を手動指定 |
| `--save-ext 拡張子` | 自動保存時の拡張子をカスタム指定 |

### 対応ファイル形式

- **CSV** (`.csv`) - カンマ区切り
- **TSV** (`.tsv`) - タブ区切り  
- **PSV** (`.psv`) - パイプ区切り
- **カスタム** - `-d`オプションで任意の区切り文字

### 対応エンコーディング

以下のエンコーディングを自動検出・対応：
- UTF-8
- Shift_JIS
- CP932（Windows日本語）
- EUC-JP（Unix日本語）
- ISO-2022-JP（JISコード）
- UTF-16
- Latin-1
- CP1252（Windows西欧）

## 🌏 Unicode・日本語対応

このツールは特に日本語を含むCJK（中国語・日本語・韓国語）テキストに優れた対応を提供します：

- **正確な幅計算**: Unicode East Asian Widthプロパティを使用
- **全角文字処理**: 表示列数2の文字を正確に処理
- **全角スペース修正**: `--normalize-ws`オプションでターミナル依存の表示問題を解決

### 日本語データでの使用例
```bash
# 全角スペースが含まれるファイルで表示が崩れる場合
python table_converter.py japanese_data.csv --normalize-ws --save
```

## 📁 自動保存の例

```bash
# data.csv → data.txt（ASCII形式）
python table_converter.py data.csv --save

# data.csv → data.md（マークダウン形式） 
python table_converter.py data.csv --format markdown --save

# data.csv → data.out（カスタム拡張子）
python table_converter.py data.csv --save --save-ext .out
```

## 🔧 インストール

外部依存なし！Python標準ライブラリのみ使用。

```bash
# レポジトリをクローン
git clone https://github.com/crt-ikeda/csv-table-converter.git
cd csv-table-converter

# 実行可能にする（オプション）
chmod +x table_converter.py

# 実行
python table_converter.py your_file.csv
```

## 📄 動作要件

- Python 3.6以上
- 外部依存なし（標準ライブラリのみ）

## 💡 実用的な活用例

### データ分析
```bash
# 分析結果をMarkdown形式で保存してNotionに貼り付け
python table_converter.py analysis_result.csv --format markdown --save
```

### レポート作成
```bash
# 列幅を制限してコンパクトな表を作成
python table_converter.py report_data.csv --max-width 15 --save
```

### バッチ処理
```bash
# 複数ファイルを一括変換（bash例）
for file in *.csv; do
    python table_converter.py "$file" --normalize-ws --save
done
```

### GitHub/Notion対応
```bash
# GitHubのREADMEに貼り付け用のマークダウン表
python table_converter.py stats.csv --format markdown --no-align
```

## 🛠️ 技術的特徴

### 全角文字の正確な表示幅計算
```python
# Unicode East Asian Widthを使用した精密な幅計算
eaw = unicodedata.east_asian_width(char)
if eaw in ('F', 'W'):  # 全角文字
    width += 2
else:  # 半角文字
    width += 1
```

### 全角スペース問題の解決
環境によって表示幅が異なる全角スペース（`　`）を半角スペース2個に正規化することで、どの環境でも安定した表示を実現。

### エンコーディング自動判定
8種類のエンコーディングを順次試行し、最適なエンコーディングで自動読み込み。

## 🤝 コントリビューション

プルリクエストやイシューを歓迎します！改善提案がございましたらお気軽にご連絡ください。

## 📜 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご確認ください。

## 🙏 謝辞

- Pythonコミュニティの素晴らしい標準ライブラリツール群
- Unicode Consortiumの East Asian Width仕様
- このツールを使用・改善してくださるすべてのユーザーの皆様

---

**データ分析・レポート作成・美しい表表示が必要なあらゆる場面で活用してください！📊✨**