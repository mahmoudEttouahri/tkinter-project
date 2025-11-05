# Scientific Publications Explorer

A desktop application for exploring, filtering, and analyzing scientific publication data from CSV files.

## Features

- **Load & Browse** - Import CSV files containing publication data
- **Preprocessing** - Standardize author names and venue names automatically
- **Search & Filter** - Filter publications by title, author, year, or venue
- **Visualize** - Generate charts showing publication trends and top authors
- **Export** - Save filtered results to CSV

## Requirements

```
python 3.x
pandas
matplotlib
tkinter (usually included with Python)
```

## Installation

1. Install required packages:
```bash
pip install pandas matplotlib
```

2. Run the application:
```bash
python main.py
```

## Usage

1. **Load Data** - Click "Load CSV" and select your publications CSV file
2. **Preprocess** - Click "Run Preprocessing" to standardize author and venue names
3. **Filter** - Enter search terms in any field (Title, Author, Year, Venue) and click "Apply Filter"
4. **Visualize** - Click "Analyze & Visualize" to see publication trends and top authors
5. **Export** - Click "Export Results" to save filtered data

## CSV Format

Your CSV file should contain these columns (case-insensitive):
- **Title** - Publication title
- **Authors** - Author names (comma-separated)
- **Year** - Publication year
- **Venue** - Conference or journal name

## License

MIT
