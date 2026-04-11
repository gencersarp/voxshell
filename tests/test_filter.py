from voxshell.filter import clean_for_speech


class TestBasicStripping:
    def test_empty(self):
        assert clean_for_speech('') == ''

    def test_whitespace_only(self):
        assert clean_for_speech('   \n\n  ') == ''

    def test_plain_sentence_passes_through(self):
        result = clean_for_speech('The build completed successfully.')
        assert 'build completed successfully' in result

    def test_ansi_stripped(self):
        result = clean_for_speech('\x1b[32mAll tests passed.\x1b[0m')
        assert '\x1b' not in result
        assert 'All tests passed' in result

    def test_cr_overwrite_removed(self):
        # Progress bar: "50%\r100%\n"
        result = clean_for_speech('50%\r100%\nAll done.')
        assert 'All done' in result
        # "50%" should not appear (overwritten)
        assert '50%' not in result


class TestCodeRemoval:
    def test_fenced_code_block_removed(self):
        text = 'Here is the fix.\n```python\ndef foo():\n    pass\n```\nLooks good.'
        result = clean_for_speech(text)
        assert 'def foo' not in result
        assert 'Here is the fix' in result

    def test_inline_code_removed(self):
        result = clean_for_speech('Run `pip install voxshell` to install.')
        assert '`' not in result

    def test_indented_code_removed(self):
        text = 'The output is:\n    some_var = 42\nFinished.'
        result = clean_for_speech(text)
        assert 'some_var' not in result


class TestPathAndUrlRemoval:
    def test_unix_path_removed(self):
        result = clean_for_speech('Saved the file to /Users/alice/project/main.py.')
        assert '/Users/alice' not in result

    def test_tilde_path_removed(self):
        result = clean_for_speech('Config is at ~/config/settings.json.')
        assert '~/config' not in result

    def test_url_removed(self):
        result = clean_for_speech('See https://docs.python.org/3/ for details.')
        assert 'https://' not in result
        assert 'docs.python.org' not in result


class TestMarkdownStripping:
    def test_header_text_kept(self):
        result = clean_for_speech('## Summary\nThe task is done.')
        assert '##' not in result
        assert 'Summary' in result or 'task is done' in result

    def test_bold_text_kept(self):
        result = clean_for_speech('The **most important** thing is clarity.')
        assert '**' not in result
        assert 'most important' in result

    def test_link_label_kept(self):
        result = clean_for_speech('Read the [official docs](https://example.com).')
        assert 'official docs' in result
        assert 'https://' not in result

    def test_image_removed(self):
        result = clean_for_speech('Here is a diagram: ![arch](arch.png). Done.')
        assert '![' not in result


class TestLineFiltering:
    def test_diff_lines_skipped(self):
        text = '+++ new line\n--- old line\nAll changes applied.'
        result = clean_for_speech(text)
        assert '+++' not in result
        assert 'All changes applied' in result

    def test_shell_prompt_lines_skipped(self):
        text = '$ git commit -m "fix"\nCommit created successfully.'
        result = clean_for_speech(text)
        assert '$' not in result
        assert 'Commit created successfully' in result

    def test_low_alpha_ratio_skipped(self):
        # Line of mostly symbols
        result = clean_for_speech('=====>>>> 0x1f3a2 <<<<=====\nDone.')
        assert '=====' not in result


class TestSentenceLimit:
    def test_max_sentences_default(self):
        long_text = ' '.join([f'Sentence {i}.' for i in range(20)])
        result = clean_for_speech(long_text)
        # Default max_sentences=3: at most 3 sentences
        count = result.count('.')
        assert count <= 3

    def test_custom_max_sentences(self):
        long_text = ' '.join([f'Sentence {i}.' for i in range(20)])
        result = clean_for_speech(long_text, max_sentences=5)
        count = result.count('.')
        assert count <= 5


class TestXmlTagRemoval:
    def test_tool_use_block_removed(self):
        text = 'Processing.<tool_use>\n{"name": "read_file"}\n</tool_use>\nDone.'
        result = clean_for_speech(text)
        assert 'tool_use' not in result
        assert 'read_file' not in result
