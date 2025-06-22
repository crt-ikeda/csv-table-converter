#!/usr/bin/env python3
"""
CSV/TSV/PSVファイルをASCII形式またはマークダウン形式の表に変換するスクリプト

使用例:
    python table_converter.py data.csv
    python table_converter.py data.tsv -o output.txt
    python table_converter.py data.csv --format markdown
    python table_converter.py data.psv --max-width 20 --normalize-ws
"""

import csv
import argparse
import sys
import unicodedata
from pathlib import Path


def get_display_width(text):
    """文字列の実際の表示幅を計算（全角文字対応、全角スペース問題対策）"""
    width = 0
    for char in text:
        # 全角スペースの特別処理
        if char == '\u3000':  # 全角スペース
            width += 2
        else:
            # East Asian Widthを取得
            eaw = unicodedata.east_asian_width(char)
            if eaw in ('F', 'W'):  # Fullwidth, Wide
                width += 2
            elif eaw in ('H', 'Na', 'N'):  # Halfwidth, Narrow, Neutral
                width += 1
            else:  # Ambiguous
                # 通常は1文字として扱うが、環境によっては2文字の場合もある
                width += 1
    return width


def normalize_whitespace(text, visible_mode=False):
    """全角スペースを正規化（オプションで可視化）"""
    if visible_mode:
        # 全角スペースを可視化（デバッグ用）
        return text.replace('\u3000', '□')
    else:
        # 全角スペースを半角スペース2個に置換（表示安定化）
        return text.replace('\u3000', '  ')


def truncate_text_by_width(text, max_width, normalize_ws=False):
    """表示幅を考慮してテキストを切り詰める"""
    if normalize_ws:
        text = normalize_whitespace(text)
    
    if get_display_width(text) <= max_width:
        return text
    
    result = ""
    current_width = 0
    
    for char in text:
        if char == '\u3000':
            char_width = 2
        else:
            char_width = 2 if unicodedata.east_asian_width(char) in ('F', 'W') else 1
        
        if current_width + char_width > max_width - 3:  # "..."分を予約
            result += "..."
            break
        result += char
        current_width += char_width
    
    return result


def pad_text_to_width(text, target_width, normalize_ws=False):
    """表示幅を考慮して文字列をパディング"""
    if normalize_ws:
        text = normalize_whitespace(text)
    
    current_width = get_display_width(text)
    if current_width >= target_width:
        return text
    
    # 不足分を半角スペースで埋める
    padding = ' ' * (target_width - current_width)
    return text + padding


def detect_delimiter(file_path):
    """ファイル拡張子から区切り文字を判定"""
    suffix = Path(file_path).suffix.lower()
    if suffix == '.csv':
        return ','
    elif suffix == '.tsv':
        return '\t'
    elif suffix == '.psv':
        return '|'
    else:
        # デフォルトはカンマ
        return ','


def read_delimited_file(file_path, delimiter=None):
    """区切り文字ファイルを読み込んでリストのリストとして返す"""
    if delimiter is None:
        delimiter = detect_delimiter(file_path)
    
    # 試行するエンコーディングのリスト（優先順）
    encodings = [
        'utf-8',
        'shift_jis',
        'cp932',        # Windows日本語（Shift_JISの拡張）
        'euc-jp',       # Unix/Linux日本語
        'iso-2022-jp',  # JISコード
        'utf-16',       # Unicode 16bit
        'latin-1',      # ISO-8859-1（バイナリセーフ）
        'cp1252',       # Windows西欧
    ]
    
    last_error = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, newline='') as file:
                # まずSnifferで区切り文字を自動検出を試行
                sample = file.read(1024)
                file.seek(0)
                
                try:
                    sniffer = csv.Sniffer()
                    detected_delimiter = sniffer.sniff(sample).delimiter
                    if detected_delimiter in [',', '\t', '|', ';']:
                        delimiter = detected_delimiter
                except:
                    pass  # 検出失敗時は指定された区切り文字を使用
                
                reader = csv.reader(file, delimiter=delimiter)
                data = list(reader)
                
                # 成功時はエンコーディングを報告
                print(f"エンコーディング: {encoding} で読み込み成功", file=sys.stderr)
                return data
                
        except UnicodeDecodeError as e:
            last_error = e
            print(f"エンコーディング {encoding} で失敗: {str(e)[:100]}...", file=sys.stderr)
            continue
        except Exception as e:
            last_error = e
            print(f"エンコーディング {encoding} で予期しないエラー: {str(e)[:100]}...", file=sys.stderr)
            continue
    
    # すべてのエンコーディングで失敗した場合
    print(f"\nエラー: ファイル '{file_path}' を読み込めませんでした。", file=sys.stderr)
    print("試行したエンコーディング:", ', '.join(encodings), file=sys.stderr)
    if last_error:
        print(f"最後のエラー: {last_error}", file=sys.stderr)
    
    # 最後の手段：ファイルの先頭を16進ダンプで表示
    try:
        with open(file_path, 'rb') as f:
            first_bytes = f.read(32)
            hex_dump = ' '.join(f'{b:02x}' for b in first_bytes)
            print(f"ファイル先頭32バイト: {hex_dump}", file=sys.stderr)
    except:
        pass
    
    raise UnicodeDecodeError(
        "unknown", b"", 0, 1, 
        f"ファイル '{file_path}' は対応していないエンコーディングです。"
    )


def detect_header(data, delimiter):
    """ヘッダーの有無を自動検出"""
    if not data or len(data) < 2:
        return False
    
    try:
        # CSV Snifferを使ってヘッダーの存在を検出
        sample_data = []
        for row in data[:10]:  # 最初の10行をサンプルとして使用
            sample_data.append(delimiter.join(row))
        sample_text = '\n'.join(sample_data)
        
        sniffer = csv.Sniffer()
        return sniffer.has_header(sample_text)
    except:
        # 検出失敗時は最初の行が数値のみかどうかで判定
        first_row = data[0]
        for cell in first_row:
            try:
                float(cell)
            except ValueError:
                # 数値でないセルがあればヘッダーの可能性が高い
                return True
        return False


def calculate_column_widths(data, max_width=None, normalize_ws=False):
    """各列の最適な幅を計算（全角文字対応）"""
    if not data:
        return []
    
    num_cols = len(data[0])
    widths = [0] * num_cols
    
    # 各列の最大表示幅を計算
    for row in data:
        for i, cell in enumerate(row):
            if i < num_cols:
                cell_text = str(cell) if cell is not None else ''
                if max_width:
                    cell_text = truncate_text_by_width(cell_text, max_width, normalize_ws)
                if normalize_ws:
                    cell_text = normalize_whitespace(cell_text)
                display_width = get_display_width(cell_text)
                widths[i] = max(widths[i], display_width)
    
    # 最低幅を3文字に設定
    return [max(w, 3) for w in widths]


def escape_markdown_pipes(text):
    """マークダウン表内でパイプ文字をエスケープ"""
    return str(text).replace('|', '\\|') if text is not None else ''


def create_markdown_table(data, max_width=None, has_header=True, normalize_ws=False, align_columns=True):
    """データをマークダウン表形式に変換"""
    if not data:
        return "空のデータです。"
    
    processed_data = []
    
    # データを前処理
    for row in data:
        processed_row = []
        for cell in row:
            cell_text = escape_markdown_pipes(cell)
            if max_width:
                cell_text = truncate_text_by_width(cell_text, max_width, normalize_ws)
            if normalize_ws:
                cell_text = normalize_whitespace(cell_text)
            processed_row.append(cell_text)
        processed_data.append(processed_row)
    
    if not processed_data:
        return "空のデータです。"
    
    lines = []
    
    # 列幅を計算（揃える場合のみ）
    if align_columns:
        widths = calculate_column_widths(processed_data, max_width, normalize_ws)
    
    # 各行を処理
    for row_idx, row in enumerate(processed_data):
        if align_columns:
            # 列を揃えて表示
            aligned_cells = []
            for i, cell in enumerate(row):
                if i < len(widths):
                    padded_cell = pad_text_to_width(str(cell), widths[i], normalize_ws)
                    aligned_cells.append(padded_cell)
                else:
                    aligned_cells.append(str(cell))
            line = '| ' + ' | '.join(aligned_cells) + ' |'
        else:
            # 最小限の形式
            line = '| ' + ' | '.join(str(cell) for cell in row) + ' |'
        
        lines.append(line)
        
        # ヘッダー行の後に区切り行を追加
        if has_header and row_idx == 0:
            if align_columns:
                separator_cells = ['-' * w for w in widths[:len(row)]]
                separator = '| ' + ' | '.join(separator_cells) + ' |'
            else:
                separator_cells = ['---'] * len(row)
                separator = '| ' + ' | '.join(separator_cells) + ' |'
            lines.append(separator)
    
    return '\n'.join(lines)


def create_ascii_table(data, max_width=None, has_header=True, normalize_ws=False):
    """データをASCII表形式に変換（全角文字対応）"""
    if not data:
        return "空のデータです。"
    
    # 列幅を計算
    widths = calculate_column_widths(data, max_width, normalize_ws)
    
    # 区切り線を作成
    separator = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
    
    lines = []
    lines.append(separator)
    
    for row_idx, row in enumerate(data):
        # 行の内容を作成
        row_parts = []
        for i, cell in enumerate(row):
            if i < len(widths):
                cell_text = str(cell) if cell is not None else ''
                if max_width:
                    cell_text = truncate_text_by_width(cell_text, max_width, normalize_ws)
                # 表示幅を考慮してパディング
                padded_cell = pad_text_to_width(cell_text, widths[i], normalize_ws)
                row_parts.append(f' {padded_cell} ')
        
        line = '|' + '|'.join(row_parts) + '|'
        lines.append(line)
        
        # ヘッダー行の後に区切り線を追加（ヘッダーがある場合のみ）
        if has_header and row_idx == 0:
            lines.append(separator)
    
    lines.append(separator)
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='CSV/TSV/PSVファイルをASCII表形式またはマークダウン表形式で表示',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s data.csv                         # CSVファイルをASCII表で画面表示
  %(prog)s data.tsv -o table.txt            # TSVファイルをASCII表でファイル保存
  %(prog)s data.csv --format markdown       # マークダウン表形式で出力
  %(prog)s data.csv --format markdown -o table.md  # マークダウン表をファイル保存
  %(prog)s data.csv --save                  # data.txt として自動保存
  %(prog)s data.csv --format markdown --save  # data.md として自動保存
  %(prog)s data.psv --max-width 15          # 列幅を15文字に制限
  %(prog)s data.csv -d ";"                  # セミコロン区切りとして処理
  %(prog)s data.csv --no-header             # ヘッダーなしとして処理
  %(prog)s data.csv --header                # 強制的にヘッダーありとして処理
  %(prog)s data.csv --normalize-ws          # 全角スペースを半角スペース2個に変換
  %(prog)s data.csv --format markdown --no-align  # マークダウン表（最小形式）
        """
    )
    
    parser.add_argument('input_file', help='入力ファイル (.csv, .tsv, .psv)')
    parser.add_argument('-d', '--delimiter', help='区切り文字を手動指定')
    parser.add_argument('--max-width', type=int, help='各列の最大文字数')
    parser.add_argument('--encoding', default='utf-8', 
                       help='文字エンコーディング (default: utf-8)')
    parser.add_argument('--normalize-ws', action='store_true',
                       help='全角スペースを半角スペース2個に変換（表示安定化）')
    parser.add_argument('--format', choices=['ascii', 'markdown'], default='ascii',
                       help='出力形式を選択 (default: ascii)')
    parser.add_argument('--no-align', action='store_true',
                       help='マークダウン形式で列を揃えない（最小形式）')
    parser.add_argument('--save-ext', 
                       help='--saveオプション使用時の拡張子を手動指定（例: --save-ext .out）')
    
    # ヘッダー関連オプション
    header_group = parser.add_mutually_exclusive_group()
    header_group.add_argument('--header', action='store_true', 
                             help='強制的にヘッダーありとして処理')
    header_group.add_argument('--no-header', action='store_true', 
                             help='ヘッダーなしとして処理')
    
    # 出力先オプション（相互排他）
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-o', '--output', help='出力ファイル名（指定しない場合は画面表示）')
    output_group.add_argument('--save', action='store_true',
                             help='元ファイル名の拡張子を変更して自動保存（ASCII形式: .txt, マークダウン形式: .md）')
    
    args = parser.parse_args()
    
    # ファイルの存在確認
    if not Path(args.input_file).exists():
        print(f"エラー: ファイル '{args.input_file}' が見つかりません。", file=sys.stderr)
        sys.exit(1)
    
    try:
        # ファイル読み込み
        print(f"'{args.input_file}' を読み込み中...", file=sys.stderr)
        data = read_delimited_file(args.input_file, args.delimiter)
        
        if not data:
            print("エラー: ファイルが空です。", file=sys.stderr)
            sys.exit(1)
        
        print(f"読み込み完了: {len(data)}行, {len(data[0])}列", file=sys.stderr)
        
        # ヘッダーの有無を判定
        if args.header:
            has_header = True
            print("ヘッダーありとして処理します。", file=sys.stderr)
        elif args.no_header:
            has_header = False
            print("ヘッダーなしとして処理します。", file=sys.stderr)
        else:
            # 自動検出
            delimiter = args.delimiter or detect_delimiter(args.input_file)
            has_header = detect_header(data, delimiter)
            if has_header:
                print("ヘッダーを検出しました。", file=sys.stderr)
            else:
                print("ヘッダーが検出されませんでした。", file=sys.stderr)
        
        # 出力形式の通知
        if args.format == 'markdown':
            print("マークダウン表形式で出力します。", file=sys.stderr)
            if args.no_align:
                print("列を揃えない最小形式を使用します。", file=sys.stderr)
        else:
            print("ASCII表形式で出力します。", file=sys.stderr)
        
        # 全角スペース正規化の通知
        if args.normalize_ws:
            print("全角スペースを半角スペース2個に変換します。", file=sys.stderr)
        
        # 出力先を決定
        output_path = None
        if args.output:
            output_path = args.output
        elif args.save:
            # 自動保存の場合、拡張子を決定
            input_path = Path(args.input_file)
            if args.save_ext:
                # 手動指定の拡張子
                new_ext = args.save_ext if args.save_ext.startswith('.') else f'.{args.save_ext}'
            else:
                # 自動拡張子
                if args.format == 'markdown':
                    new_ext = '.md'
                else:
                    new_ext = '.txt'
            
            output_path = input_path.with_suffix(new_ext)
            print(f"自動保存ファイル名: {output_path}", file=sys.stderr)
        
        # 表を生成
        if args.format == 'markdown':
            table = create_markdown_table(
                data, 
                args.max_width, 
                has_header, 
                args.normalize_ws,
                not args.no_align  # no_alignが指定されていなければ揃える
            )
        else:
            table = create_ascii_table(data, args.max_width, has_header, args.normalize_ws)
        
        # 出力
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(table)
            print(f"表を '{output_path}' に保存しました。", file=sys.stderr)
        else:
            print(table)
            
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
