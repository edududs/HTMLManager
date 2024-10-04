from unittest.mock import MagicMock

import pytest

from main import HTMLProcessor, main


@pytest.fixture
def mock_html_processor(mocker):
    mock_html_processor_class = mocker.patch("main.HTMLProcessor")
    mock_html_processor = MagicMock()
    mock_html_processor_class.return_value = mock_html_processor
    return mock_html_processor


@pytest.mark.parametrize(
    "user_input, expected_method, expected_message",
    [
        ("0", "process", "Cleaning HTML content..."),
        ("1", "process", "Removing tables..."),
        ("2", "process", "Separating and removing tables..."),
        ("3", "save_only_content", "Saving content..."),
    ],
)
def test_main_options(
    mock_html_processor,
    user_input,
    expected_method,
    expected_message,
    capfd,
    monkeypatch,
):
    monkeypatch.setattr("builtins.input", lambda _: user_input)
    main()

    # Verificando o método correto chamado
    if expected_method == "process":
        mock_html_processor.process.assert_called_once()
    else:
        getattr(mock_html_processor, expected_method).assert_called_once()

    # Verificando as saídas no terminal
    captured = capfd.readouterr()
    assert expected_message in captured.out
    assert "Process completed." in captured.out


def test_main_no_file_selected(capfd, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    main()

    # Verificando se a mensagem correta foi exibida
    captured = capfd.readouterr()
    assert "No file selected." in captured.out


def test_main_file_not_found(mocker, capfd, monkeypatch):
    mocker.patch(
        "main.HTMLProcessor", side_effect=FileNotFoundError("The file does not exist.")
    )
    monkeypatch.setattr("builtins.input", lambda _: "/path/to/invalid/file.html")
    main()

    # Verificando se a mensagem de erro foi exibida
    captured = capfd.readouterr()
    assert "Error initializing HTMLProcessor: The file does not exist." in captured.out


def test_main_invalid_file_type(mocker, capfd, monkeypatch):
    mocker.patch(
        "main.HTMLProcessor", side_effect=ValueError("The file is not an HTML file.")
    )
    monkeypatch.setattr("builtins.input", lambda _: "/path/to/invalid/file.txt")
    main()

    # Verificando se a mensagem de erro foi exibida
    captured = capfd.readouterr()
    assert (
        "Error initializing HTMLProcessor: The file is not an HTML file."
        in captured.out
    )


def test_main_multiple_options(mock_html_processor, capfd, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "0 1 2 3")
    main()

    # Verificando os métodos chamados
    mock_html_processor.process.assert_any_call()
    mock_html_processor.process.assert_any_call(separate_tables=True)
    mock_html_processor.save_only_content.assert_called_once()

    # Verificando as saídas no terminal
    captured = capfd.readouterr()
    assert "Saving content..." in captured.out
    assert "Cleaning HTML content..." in captured.out
    assert "Separating and removing tables..." in captured.out
    assert "Process completed." in captured.out
