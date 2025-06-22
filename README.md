# CSV Table Converter

Convert CSV/TSV/PSV files to beautiful ASCII tables or Markdown tables with full Unicode support.

## ✨ Features

- **Multiple Output Formats**: ASCII tables and Markdown tables
- **Full Unicode Support**: Perfect handling of Japanese, Chinese, Korean, and other Unicode characters
- **Smart Auto-Detection**: Automatic delimiter and header detection
- **Multiple Encodings**: Supports UTF-8, Shift_JIS, CP932, EUC-JP, and more
- **Auto-Save**: Generate output files with automatic naming
- **Full-Width Character Support**: Correctly handles full-width spaces and characters
- **Flexible Options**: Column width limits, custom delimiters, and more

## 🚀 Quick Start

```bash
# Basic usage - display as ASCII table
python table_converter.py data.csv

# Save as text file automatically
python table_converter.py data.csv --save

# Generate Markdown table
python table_converter.py data.csv --format markdown --save

# Handle full-width spaces (for CJK text)
python table_converter.py data.csv --normalize-ws --save
```

## 📋 Examples

### Input CSV
```csv
Name,Age,City
田中太郎,25,東京
鈴木花子,30,大阪
佐藤次郎,28,福岡
```

### ASCII Table Output
```
+----------+------+------+
| Name     | Age  | City |
+----------+------+------+
| 田中太郎 | 25   | 東京 |
| 鈴木花子 | 30   | 大阪 |
| 佐藤次郎 | 28   | 福岡 |
+----------+------+------+
```

### Markdown Table Output
```markdown
| Name     | Age  | City |
|----------|------|------|
| 田中太郎 | 25   | 東京 |
| 鈴木花子 | 30   | 大阪 |
| 佐藤次郎 | 28   | 福岡 |
```

## 📖 Usage

```bash
python table_converter.py [OPTIONS] INPUT_FILE
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output FILE` | Output file name |
| `--save` | Auto-save with automatic file naming |
| `--format {ascii,markdown}` | Output format (default: ascii) |
| `--normalize-ws` | Normalize full-width spaces for stable display |
| `--max-width N` | Limit column width to N characters |
| `--no-align` | Minimal Markdown format without column alignment |
| `--header` | Force treat first row as header |
| `--no-header` | Force treat all rows as data |
| `-d CHAR` | Manually specify delimiter |
| `--save-ext EXT` | Custom extension for auto-save |

### File Format Support

- **CSV** (`.csv`) - Comma-separated values
- **TSV** (`.tsv`) - Tab-separated values  
- **PSV** (`.psv`) - Pipe-separated values
- **Custom** - Any delimiter with `-d` option

### Encoding Support

Automatically detects and handles:
- UTF-8
- Shift_JIS
- CP932 (Windows Japanese)
- EUC-JP (Unix Japanese)
- ISO-2022-JP (JIS)
- UTF-16
- Latin-1
- CP1252 (Windows Western)

## 🌏 Unicode & CJK Support

This tool provides excellent support for Unicode characters, especially CJK (Chinese, Japanese, Korean) text:

- **Accurate Width Calculation**: Uses Unicode East Asian Width properties
- **Full-Width Character Handling**: Properly displays characters that take 2 display columns
- **Full-Width Space Fix**: `--normalize-ws` option solves terminal-dependent display issues

### Example with Japanese Text
```bash
# For files containing full-width spaces that might display incorrectly
python table_converter.py japanese_data.csv --normalize-ws --save
```

## 📁 Auto-Save Examples

```bash
# data.csv → data.txt (ASCII format)
python table_converter.py data.csv --save

# data.csv → data.md (Markdown format) 
python table_converter.py data.csv --format markdown --save

# data.csv → data.out (custom extension)
python table_converter.py data.csv --save --save-ext .out
```

## 🔧 Installation

No additional dependencies required! Uses only Python standard library.

```bash
# Clone the repository
git clone https://github.com/crt-ikeda/csv-table-converter.git
cd csv-table-converter

# Make executable (optional)
chmod +x table_converter.py

# Run
python table_converter.py your_file.csv
```

## 📄 Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to the Python community for excellent standard library tools
- Unicode Consortium for East Asian Width specifications
- All contributors and users of this tool

---

**Perfect for data analysis, report generation, and anywhere you need beautiful table display! 📊✨**