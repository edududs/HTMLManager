import os
from itertools import count
from pathlib import Path

try:
    import trafilatura
    from bs4 import BeautifulSoup
except ImportError as e:
    print("\033[91m" + f"Error importing libraries: {e}" + "\033[0m")
    print("\033[93m" + "Please install the required libraries using:" + "\033[0m")
    print("\033[96m" + "pip install -r requirements.txt" + "\033[0m")

BASE_DIR = Path(__file__).resolve().parent
FILES = Path.home() / "Documents"

os.makedirs(FILES, exist_ok=True)


class Cleaner:
    def __init__(self, content):
        self.content = content

    def remove_empty_tags(self) -> None:
        """
        Removes empty tags from the HTML content.
        A tag is considered empty if it does not contain any text content.
        """
        for tag in self.content.find_all():
            if not tag.get_text(strip=True):
                tag.decompose()

    def remove_all_divs(self) -> None:
        """
        Removes all <div> tags from the HTML content.
        """
        for div in self.content.find_all("div"):
            div.unwrap()

    def remove_answers(self) -> None:
        """
        Removes answers from the HTML content.
        """
        for paragraph in self.content.find_all("p"):
            if paragraph.get_text().strip().startswith(
                "Resposta pe"
            ) or paragraph.get_text().strip().startswith("Respostas pe"):
                paragraph.decompose()

    def remove_all_classes(self) -> None:
        """
        Removes all classes from the HTML content.
        """
        for tag in self.content.find_all(class_=True):
            del tag["class"]

    def remove_all_ids(self) -> None:
        """
        Removes all IDs from the HTML content.
        """
        for tag in self.content.find_all(id=True):
            del tag["id"]

    def remove_lang_attributes(self) -> None:
        """Removes the 'lang' attribute from all tags in the parsed HTML file."""
        for tag in self.content.find_all(lang=True):
            del tag["lang"]

    def remove_spans_tags(self) -> None:
        """
        Removes all <span> tags from the parsed HTML file.
        """
        for tag in self.content.find_all("span"):
            tag.unwrap()

    def remove_imgs_tags(self) -> None:
        """Removes all <img> tags from the HTML content."""
        for tag in self.content.find_all("img"):
            tag.decompose()

    def wrap_paragraph_with_div(self) -> None:
        """
        Identifies paragraphs containing images, removes the images, and wraps the paragraph in a div with the class 'exercise'.
        """
        for paragraph in self.content.find_all("p"):
            if paragraph.find("img"):
                div_wrapper = self.content.new_tag("div", **{"class": "exercise"})
                paragraph.wrap(div_wrapper)

    def clean_empty_tables(self) -> None:
        """
        Removes empty <table> tags from the HTML content.
        A table is considered empty if it contains only tags without any text content.
        """
        for table in self.content.find_all("table"):
            # Check if all descendants of the table have no text content
            if not any(
                descendant.get_text(strip=True) for descendant in table.descendants
            ):
                table.decompose()

    def clean_empty_colgroups(self) -> None:
        """
        Removes empty <colgroup> tags from the HTML content.
        A colgroup is considered empty if it does not contain any <col> tags.
        """
        for colgroup in self.content.find_all("colgroup"):
            if not colgroup.find_all("col"):
                colgroup.decompose()

    def clean(
        self,
        remove_lang: bool = True,
        remove_spans: bool = True,
        remove_imgs: bool = True,
        clean_empty_tables: bool = True,
        clean_empty_colgroups: bool = True,
        wrap_images: bool = True,
        remove_classes: bool = True,
        remove_ids: bool = True,
    ) -> BeautifulSoup:
        """
        Cleans the HTML content following a specific order:
        - First removes 'lang' attributes and empty tables.
        - Then wraps paragraphs containing images in a div with the 'exercise' class.
        - Finally, removes images (after paragraph modification).

        Args:
            remove_lang (bool): Indicates if 'lang' attributes should be removed.
            remove_spans (bool): Indicates if <span> tags should be removed.
            remove_imgs (bool): Indicates if <img> tags should be removed.
            clean_empty_tables (bool): Indicates if empty <table> tags should be removed.
            clean_empty_colgroups (bool): Indicates if empty <colgroup> tags should be removed.
            wrap_images (bool): Indicates if paragraphs containing images should be wrapped in a div.

        Returns:
            BeautifulSoup: The cleaned HTML content.
        """
        self.remove_all_divs()
        if remove_lang:
            self.remove_lang_attributes()
        if clean_empty_tables:
            self.clean_empty_tables()
        if clean_empty_colgroups:
            self.clean_empty_colgroups()
        if remove_classes:
            self.remove_all_classes()
        if remove_ids:
            self.remove_all_ids()
        if wrap_images:
            self.wrap_paragraph_with_div()  # Wrap paragraphs before removing images
        if remove_spans:
            self.remove_spans_tags()
        if remove_imgs:
            self.remove_imgs_tags()

        self.remove_answers()

        self.remove_empty_tags()

        print("Cleaned HTML content.")
        return self.content


class HTMLProcessor:
    def __init__(self, file_path: str | Path) -> None:
        self.file_path = file_path if isinstance(file_path, Path) else Path(file_path)
        self.file = self.parse_html()
        self.content_html = self.extract_content_trafilatura()
        self.cleaner = Cleaner(self.file)

    def validate_file(self) -> None:
        """
        Validates the file specified by `self.file_path`.

        Raises:
            FileNotFoundError: If the file does not exist at `self.file_path`.
            ValueError: If the file is not an HTML file (i.e., does not have a .html extension).
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"The file {self.file_path} does not exist.")
        if self.file_path.suffix.lower() != ".html":
            raise ValueError(f"The file {self.file_path} is not an HTML file.")

    def parse_html(self) -> BeautifulSoup:
        """
        Parses an HTML file and returns a BeautifulSoup object.

        Returns:
            BeautifulSoup: Parsed HTML content.

        Raises:
            ValueError: If the file cannot be parsed.
        """
        self.validate_file()
        with open(self.file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        if not soup:
            raise ValueError(f"Could not parse the file {self.file_path}.")
        return soup

    def extract_content_trafilatura(self) -> str:
        """
        Extracts the readable content from the HTML file using trafilatura.

        Returns:
            str: The readable content extracted from the HTML file.
        """
        with open(self.file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        if extracted_content := trafilatura.extract(html_content):
            return extracted_content
        else:
            raise ValueError(
                f"Could not extract content from {self.file_path} using trafilatura."
            )

    def get_paragraphs_with_images(self) -> list:
        """
        Extracts paragraphs containing images.

        Returns:
            list: Paragraph elements with images.
        """
        return [
            paragraph for paragraph in self.file.find_all("p") if paragraph.find("img")
        ]

    def _write_to_file(self, path: Path, content: str) -> None:
        """
        Writes the content to the specified file path.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def save_processed_file(self) -> None:
        base_name = "file"
        extension = ".html"

        for index in count(1):
            new_file_path = FILES / f"{base_name}-{index}{extension}"
            if not new_file_path.exists():
                break

        self._write_to_file(new_file_path, str(self.file))
        print(f"File saved as: {new_file_path}")

    def remove_all_tables(self) -> None:
        """
        Removes all <table> tags from the HTML content.
        """
        for tag in self.file.find_all("table"):
            tag.decompose()

    def separate_all_tables(self) -> None:
        """
        Separates all <table> tags from the HTML content and saves them to a separate file.
        """
        self.cleaner.clean_empty_tables()

        tables = self.file.find_all("table")
        if not tables:
            print("No tables found to separate.")
            return

        tables_content = self._get_tables_content(tables)
        tables_soup = BeautifulSoup(tables_content, "html.parser")

        new_file_path = self._generate_unique_file_path("tables", ".html")
        self._write_to_file(new_file_path, str(tables_soup))
        print(f"Tables saved as: {new_file_path}")

        # Remove the tables from the original file
        for table in tables:
            table.decompose()

    def _get_tables_content(self, tables) -> str:
        """
        Joins the HTML content of all tables into a single string.
        """
        return "\n".join(str(table) for table in tables)

    def _generate_unique_file_path(self, base_name: str, extension: str) -> Path:
        """
        Generates a unique file path by appending an incrementing index to the base name.
        """
        for index in count(1):
            new_file_path = FILES / f"{base_name}-{index}{extension}"
            if not new_file_path.exists():
                return new_file_path
        return FILES / f"{base_name}-1{extension}"

    def save_only_content(self) -> None:
        """
        Saves only the content of the HTML file.
        """
        for index in count(1):
            new_file_path = FILES / f"content-{index}.html"
            if not new_file_path.exists():
                break
        self._write_to_file(new_file_path, self.content_html)

    def process(
        self,
        remove_tables: bool = False,
        separate_tables: bool = False,
        separate_content: bool = False,
        wrap_images: bool = True,
    ) -> None:
        """
        Processes the HTML content according to the provided options.
        Args:
            remove_tables (bool): Indicates if tables should be removed.
            remove_images (bool): Indicates if images should be removed.
            remove_spans (bool): Indicates if <span> tags should be removed.
            wrap_images (bool): Indicates if paragraphs containing images should be wrapped in a div.
        """
        self.cleaner.clean(wrap_images=wrap_images)
        if separate_content:
            self.save_only_content()
        if separate_tables:
            self.separate_all_tables()
        if remove_tables:
            self.remove_all_tables()

        self.save_processed_file()


if __name__ == "__main__":
    HTMLProcessor(Path("")).process()
