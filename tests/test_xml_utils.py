from __future__ import annotations

from snapline.api_adapters.soap.xml_utils import escape_xml


def test_escape_xml_escapes_special_characters():
    assert escape_xml('a&b<tag>"quote"') == "a&amp;b&lt;tag&gt;&quot;quote&quot;"
