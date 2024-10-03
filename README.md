
# HTML Cleaner and Processor

A tool to clean and process HTML files, allowing the removal of specific tags, content extraction, and saving of processed files.

## Features

- Clean up some HTML clutter.

## Installation

1. Clone the repository:
  ```bash
  git clone <repo-url>
  cd htmlmanager
  ```

2. Install the dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Usage

1. Run the script:
  ```bash
  python main.py
  ```

2. Enter the path of the HTML file when prompted.

3. Choose the desired options from the menu:
  ```
  0. Clean HTML
  1. Remove tables
  2. Separate tables
  3. Save content
  4. Exit
  ```

## Dependencies

- `trafilatura`
- `beautifulsoup4`

Install them with:
```bash
pip install -r requirements.txt
```

## License

MIT License
