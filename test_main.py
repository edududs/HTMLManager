from unittest.mock import MagicMock, patch

import pytest

from main import HTMLProcessor, main


@pytest.fixture
def mock_html_processor():
    with patch("main.HTMLProcessor") as mock_html_processor_class:
        mock_html_processor = MagicMock()
        mock_html_processor_class.return_value = mock_html_processor
        yield mock_html_processor


def test_main_cleaned_content(mock_html_processor):
    with patch("builtins.input", side_effect=["/path/to/valid/file.html", "0"]), patch(
        "builtins.print"
    ) as mock_print:
        main()
        mock_html_processor.process.assert_called_once()
        mock_print.assert_any_call("Cleaning HTML content...")
        mock_print.assert_any_call("Process completed.")


def test_main_remove_tables(mock_html_processor):
    with patch("builtins.input", side_effect=["/path/to/valid/file.html", "1"]), patch(
        "builtins.print"
    ) as mock_print:
        main()
        mock_html_processor.process.assert_called_once_with(remove_tables=True)
        mock_print.assert_any_call("Removing tables...")
        mock_print.assert_any_call("Process completed.")


def test_main_separate_tables(mock_html_processor):
    with patch("builtins.input", side_effect=["/path/to/valid/file.html", "2"]), patch(
        "builtins.print"
    ) as mock_print:
        main()
        mock_html_processor.process.assert_called_once_with(separate_tables=True)
        mock_print.assert_any_call("Separating and removing tables...")
        mock_print.assert_any_call("Process completed.")


def test_main_save_content(mock_html_processor):
    with patch("builtins.input", side_effect=["/path/to/valid/file.html", "3"]), patch(
        "builtins.print"
    ) as mock_print:
        main()
        mock_html_processor.save_only_content.assert_called_once()
        mock_print.assert_any_call("Saving content...")
        mock_print.assert_any_call("Process completed.")


def test_main_no_file_selected():
    with patch("builtins.input", side_effect=[""]), patch(
        "builtins.print"
    ) as mock_print:
        main()
        mock_print.assert_any_call("No file selected.")


def test_main_file_not_found():
    with patch("builtins.input", side_effect=["/path/to/invalid/file.html"]), patch(
        "main.HTMLProcessor", side_effect=FileNotFoundError("The file does not exist.")
    ), patch("builtins.print") as mock_print:
        main()
        mock_print.assert_any_call(
            "Error initializing HTMLProcessor: The file does not exist."
        )


def test_main_invalid_file_type():
    with patch("builtins.input", side_effect=["/path/to/invalid/file.txt"]), patch(
        "main.HTMLProcessor", side_effect=ValueError("The file is not an HTML file.")
    ), patch("builtins.print") as mock_print:
        main()
        mock_print.assert_any_call(
            "Error initializing HTMLProcessor: The file is not an HTML file."
        )


def test_main_multiple_options(mock_html_processor):
    with patch(
        "builtins.input", side_effect=["/path/to/valid/file.html", "0 1 2 3"]
    ), patch("builtins.print") as mock_print:
        main()
        mock_html_processor.process.assert_any_call()
        mock_html_processor.process.assert_any_call(separate_tables=True)
        mock_html_processor.save_only_content.assert_called_once()
        mock_print.assert_any_call("Saving content...")
        mock_print.assert_any_call("Cleaning HTML content...")
        mock_print.assert_any_call("Separating and removing tables...")
        mock_print.assert_any_call("Process completed.")
