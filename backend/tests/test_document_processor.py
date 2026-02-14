"""
Unit tests for DocumentProcessor — file reading, text chunking, and course parsing.
"""

import os
import tempfile

import pytest

from document_processor import DocumentProcessor
from models import Course, CourseChunk


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def processor():
    """Default document processor with reasonable settings."""
    return DocumentProcessor(chunk_size=200, chunk_overlap=50)


@pytest.fixture
def large_chunk_processor():
    """Processor with large chunk size for whole-document tests."""
    return DocumentProcessor(chunk_size=5000, chunk_overlap=0)


@pytest.fixture
def sample_course_file():
    """Create a temporary course file with valid format."""
    content = """Course Title: Test Course on AI Basics
Course Link: https://example.com/ai-basics
Course Instructor: Dr. Smith

Lesson 1: Introduction to AI
Lesson Link: https://example.com/ai-basics/lesson/1
Artificial intelligence is a broad field of computer science. It focuses on creating smart machines capable of performing tasks that typically require human intelligence. These include learning, reasoning, and self-correction.

Lesson 2: Machine Learning Fundamentals
Lesson Link: https://example.com/ai-basics/lesson/2
Machine learning is a subset of artificial intelligence. It gives computers the ability to learn from data without being explicitly programmed. Supervised and unsupervised learning are the two main types.

Lesson 3: Deep Learning
Lesson Link: https://example.com/ai-basics/lesson/3
Deep learning uses neural networks with many layers. These networks learn representations of data with multiple levels of abstraction. Convolutional neural networks and recurrent neural networks are common architectures.
"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def minimal_course_file():
    """Course file with only title, no lessons."""
    content = """Course Title: Minimal Course
Course Link: https://example.com/minimal
Course Instructor: Nobody

Just some content without lesson markers.
This is a plain text body.
"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        path = f.name
    yield path
    os.unlink(path)


# ─── File Reading Tests ──────────────────────────────────────────────────────


class TestReadFile:
    """Tests for the read_file method."""

    def test_read_utf8_file(self, processor):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("Hello, UTF-8 world! 🌍")
            path = f.name
        try:
            content = processor.read_file(path)
            assert "Hello, UTF-8 world!" in content
        finally:
            os.unlink(path)

    def test_read_empty_file(self, processor):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            path = f.name
        try:
            content = processor.read_file(path)
            assert content == ""
        finally:
            os.unlink(path)

    def test_read_nonexistent_file_raises(self, processor):
        with pytest.raises(FileNotFoundError):
            processor.read_file("/nonexistent/path/to/file.txt")


# ─── Text Chunking Tests ────────────────────────────────────────────────────


class TestChunkText:
    """Tests for the chunk_text method."""

    def test_short_text_single_chunk(self, processor):
        text = "This is a short sentence."
        chunks = processor.chunk_text(text)
        assert len(chunks) == 1
        assert "short sentence" in chunks[0]

    def test_long_text_produces_multiple_chunks(self, processor):
        # Create text longer than chunk_size
        sentences = [f"Sentence number {i} is here." for i in range(50)]
        text = " ".join(sentences)
        chunks = processor.chunk_text(text)
        assert len(chunks) > 1

    def test_chunks_not_empty(self, processor):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = processor.chunk_text(text)
        for chunk in chunks:
            assert len(chunk.strip()) > 0

    def test_overlap_creates_shared_content(self):
        """With overlap, consecutive chunks should share some text."""
        proc = DocumentProcessor(chunk_size=100, chunk_overlap=30)
        sentences = [f"This is sentence number {i} in the text." for i in range(20)]
        text = " ".join(sentences)
        chunks = proc.chunk_text(text)
        if len(chunks) >= 2:
            # At least some words from end of chunk 0 should appear in chunk 1
            words_chunk0 = set(chunks[0].split())
            words_chunk1 = set(chunks[1].split())
            overlap_words = words_chunk0 & words_chunk1
            assert len(overlap_words) > 0

    def test_no_overlap_processor(self):
        proc = DocumentProcessor(chunk_size=100, chunk_overlap=0)
        text = "A. B. C. D. E. F. G. H. I. J."
        chunks = proc.chunk_text(text)
        assert len(chunks) >= 1

    def test_whitespace_normalization(self, processor):
        text = "Sentence   with    lots   of   spaces. Another   sentence   here."
        chunks = processor.chunk_text(text)
        for chunk in chunks:
            assert "   " not in chunk  # No triple spaces

    def test_empty_text_returns_empty(self, processor):
        chunks = processor.chunk_text("")
        assert chunks == []

    def test_whitespace_only_returns_empty(self, processor):
        chunks = processor.chunk_text("   \n\t  ")
        assert chunks == []


# ─── Course Document Processing Tests ────────────────────────────────────────


class TestProcessCourseDocument:
    """Tests for parsing structured course documents."""

    def test_extracts_course_title(self, large_chunk_processor, sample_course_file):
        course, _ = large_chunk_processor.process_course_document(sample_course_file)
        assert course.title == "Test Course on AI Basics"

    def test_extracts_course_link(self, large_chunk_processor, sample_course_file):
        course, _ = large_chunk_processor.process_course_document(sample_course_file)
        assert course.course_link == "https://example.com/ai-basics"

    def test_extracts_instructor(self, large_chunk_processor, sample_course_file):
        course, _ = large_chunk_processor.process_course_document(sample_course_file)
        assert course.instructor == "Dr. Smith"

    def test_extracts_lessons(self, large_chunk_processor, sample_course_file):
        course, _ = large_chunk_processor.process_course_document(sample_course_file)
        assert len(course.lessons) == 3
        assert course.lessons[0].lesson_number == 1
        assert course.lessons[0].title == "Introduction to AI"

    def test_extracts_lesson_links(self, large_chunk_processor, sample_course_file):
        course, _ = large_chunk_processor.process_course_document(sample_course_file)
        assert course.lessons[0].lesson_link == "https://example.com/ai-basics/lesson/1"

    def test_creates_chunks(self, large_chunk_processor, sample_course_file):
        _, chunks = large_chunk_processor.process_course_document(sample_course_file)
        assert len(chunks) >= 3  # At least one chunk per lesson

    def test_chunks_have_course_title(self, large_chunk_processor, sample_course_file):
        _, chunks = large_chunk_processor.process_course_document(sample_course_file)
        for chunk in chunks:
            assert chunk.course_title == "Test Course on AI Basics"

    def test_chunks_have_lesson_numbers(
        self, large_chunk_processor, sample_course_file
    ):
        _, chunks = large_chunk_processor.process_course_document(sample_course_file)
        lesson_numbers = {c.lesson_number for c in chunks}
        assert lesson_numbers == {1, 2, 3}

    def test_chunk_indices_are_sequential(
        self, large_chunk_processor, sample_course_file
    ):
        _, chunks = large_chunk_processor.process_course_document(sample_course_file)
        indices = [c.chunk_index for c in chunks]
        assert indices == sorted(indices)

    def test_minimal_course_no_lessons(
        self, large_chunk_processor, minimal_course_file
    ):
        """File with no lesson markers should still produce chunks."""
        course, chunks = large_chunk_processor.process_course_document(
            minimal_course_file
        )
        assert course.title == "Minimal Course"
        assert len(chunks) >= 1  # Content treated as single doc

    def test_chunk_content_includes_text(
        self, large_chunk_processor, sample_course_file
    ):
        _, chunks = large_chunk_processor.process_course_document(sample_course_file)
        all_content = " ".join(c.content for c in chunks)
        assert "artificial intelligence" in all_content.lower()
        assert "machine learning" in all_content.lower()
        assert "deep learning" in all_content.lower()


# ─── Edge Cases ──────────────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_very_small_chunk_size(self):
        proc = DocumentProcessor(chunk_size=20, chunk_overlap=0)
        text = "Short. Also short. And this one too. More here."
        chunks = proc.chunk_text(text)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk) > 0

    def test_chunk_size_equals_overlap_still_makes_progress(self):
        proc = DocumentProcessor(chunk_size=50, chunk_overlap=50)
        text = "A sentence here. Another sentence. Third one. Fourth one. Fifth one."
        chunks = proc.chunk_text(text)
        # Should not infinite loop — progress is guaranteed by max(next_start, i+1)
        assert len(chunks) >= 1

    def test_single_long_sentence(self, processor):
        """A single sentence longer than chunk_size."""
        text = "A" * 500 + "."
        chunks = processor.chunk_text(text)
        assert len(chunks) >= 1
