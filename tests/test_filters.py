"""Tests for extension filtering logic."""

from catalogador.utils.filters import (
    IGNORED_EXTENSIONS,
    INCLUDED_EXTENSIONS,
    is_video,
    should_include,
)


class TestShouldInclude:
    def test_include_pdf(self):
        assert should_include(".pdf") is True

    def test_include_xlsx(self):
        assert should_include(".xlsx") is True

    def test_include_jpg(self):
        assert should_include(".jpg") is True

    def test_include_zip(self):
        assert should_include(".zip") is True

    def test_include_mp4(self):
        assert should_include(".mp4") is True

    def test_ignore_exe(self):
        assert should_include(".exe") is False

    def test_ignore_com(self):
        assert should_include(".com") is False

    def test_ignore_dll(self):
        assert should_include(".dll") is False

    def test_unknown_extension_excluded(self):
        assert should_include(".xyz") is False

    def test_case_insensitive(self):
        assert should_include(".PDF") is True
        assert should_include(".EXE") is False

    def test_ignored_takes_precedence(self):
        """If an extension is in both sets (shouldn't happen), ignored wins."""
        for ext in IGNORED_EXTENSIONS:
            assert should_include(ext) is False

    def test_all_included_pass(self):
        for ext in INCLUDED_EXTENSIONS:
            if ext not in IGNORED_EXTENSIONS:
                assert should_include(ext) is True, f"{ext} should be included"


class TestIsVideo:
    def test_mp4_is_video(self):
        assert is_video(".mp4") is True

    def test_avi_is_video(self):
        assert is_video(".avi") is True

    def test_pdf_is_not_video(self):
        assert is_video(".pdf") is False

    def test_case_insensitive(self):
        assert is_video(".MP4") is True
