from django.test.client       import Client
from django.test.utils        import override_settings

from django_nose              import FastFixtureTestCase as TestCase

from forum.views              import sanitized_smartdown as sd


ALLOWED_TAGS = [
    'a',
    'abbr',
    'acronym',
    'blockquote',
    'code',
    'del',
    'em',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'i',
    'img',
    'ins',
    'li',
    'ol',
    'p',
    'pre',
    'strong',
    'sub',
    'sup',
    'ul',
# Tables:
    'table',
    'caption',
    'thead',
    'tbody',
    'tfoot',
    'tr',
    'th',
    'td'
]

ALLOWED_ATTRIBUTES = {
    'a':       ['href', 'title'],
    'acronym': ['title'],
    'abbr':    ['title'],
    'h1':      ['id'],
    'h2':      ['id'],
    'h3':      ['id'],
    'h4':      ['id'],
    'h5':      ['id'],
    'img':     ['alt', 'id', 'src', 'title'],
    'th':      ['colspan', 'rowspan'],
    'td':      ['colspan', 'rowspan']
}


class AnchorTests(TestCase):
    """Tests the output of an anchor element."""

    def setUp(self):
        self.output = '<p><a href="http://foo.com">bar</a></p>'
        self.markdown = '[bar](http://foo.com)'
        self.title_markdown = '[bar](http://foo.com "baz")'
        self.title_html =\
            '<p><a href="http://foo.com" title="baz">bar</a></p>'

    def test_html(self):
        """Tests the HTML input of an anchor element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of an anchor element."""
        self.assertEquals(sd(self.markdown), self.output)

    def test_title_attr_html(self):
        """Tests the HTML 'title' attribute of an anchor element."""
        self.assertEquals(sd(self.title_html), self.title_html)

    def test_title_attr_markdown(self):
        """Tests the Markdown 'title' attribute of an anchor element."""
        self.assertEquals(sd(self.title_markdown), self.title_html)


class AbbrTests(TestCase):
    """Tests the output of an abbr element."""

    def setUp(self):
        self.output = '<p><abbr>foo</abbr></p>'

    def test_html(self):
        """Tests the HTML input of an abbr element."""
        self.assertEquals(sd(self.output), self.output)


class AcronymTests(TestCase):
    """Tests the output of an acronym element."""

    def setUp(self):
        self.output = '<p><acronym>foo bar</acronym></p>'
        self.title = '<p><acronym title="baz">foo bar</acronym></p>'

    def test_html(self):
        """Tests the HTML input of an acronym element."""
        self.assertEquals(sd(self.output), self.output)

    def test_title_attr(self):
        """Tests the 'title' attribute of an acronym element."""
        self.assertEquals(sd(self.title), self.title)


class BlockquoteTests(TestCase):
    """Tests the output of a blockquote element."""

    def setUp(self):
        self.output = '<blockquote>\n<p>foo</p>\n</blockquote>'
        self.markdown = '>foo'

    def test_html(self):
        """Tests the HTML input of a blockquote element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of a blockquote element."""
        self.assertEquals(sd(self.markdown), self.output)


class CodeTests(TestCase):
    """Tests the output of a code element."""

    def setUp(self):
        self.output = '<p><code>foo</code></p>'
        self.markdown = '`foo`'

    def test_html(self):
        """Tests the HTML input of a code element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of a code element."""
        self.assertEquals(sd(self.markdown), self.output)


class DeleteTests(TestCase):
    """Tests the output of a delete element."""

    def setUp(self):
        self.output = '<p><del>foo</del></p>'

    def test_html(self):
        """Tests the HTML input of a delete element."""
        self.assertEquals(sd(self.output), self.output)


class EmphasisTests(TestCase):
    """Tests the output of an emphasis element."""

    def setUp(self):
        self.output = '<p><em>foo</em></p>'
        self.markdown = '*foo*'

    def test_html(self):
        """Tests the HTML input of an emphasis element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of an emphasis element."""
        self.assertEquals(sd(self.markdown), self.output)


class Heading1Tests(TestCase):
    """Tests the output of a h1 element."""

    def setUp(self):
        self.output = '<h1>foo</h1>'
        self.markdown1 = '# foo'
        self.markdown2 = 'foo\n==='

    def test_html(self):
        """Tests the HTML input of a h1 element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown1(self):
        """Tests the '#' Markdown input of a h1 element."""
        self.assertEquals(sd(self.markdown1), self.output)

    def test_markdown2(self):
        """Tests the '===' Markdown input of a h1 element."""
        self.assertEquals(sd(self.markdown2), self.output)


class Heading2Tests(TestCase):
    """Tests the output of a h2 element."""

    def setUp(self):
        self.output = '<h2>foo</h2>'
        self.markdown1 = '## foo'
        self.markdown2 = 'foo\n---'

    def test_html(self):
        """Tests the HTML input of a h2 element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown1(self):
        """Tests the '##' Markdown input of a h2 element."""
        self.assertEquals(sd(self.markdown1), self.output)

    def test_markdown2(self):
        """Tests the '---' Markdown input of a h2 element."""
        self.assertEquals(sd(self.markdown2), self.output)


class Heading3Tests(TestCase):
    """Tests the output of a h3 element."""

    def setUp(self):
        self.output = '<h3>foo</h3>'
        self.markdown = '### foo'

    def test_html(self):
        """Tests the HTML input of a h3 element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of a h3 element."""
        self.assertEquals(sd(self.markdown), self.output)


class Heading4Tests(TestCase):
    """Tests the output of a h4 element."""

    def setUp(self):
        self.output = '<h4>foo</h4>'
        self.markdown = '#### foo'

    def test_html(self):
        """Tests the HTML input of a h4 element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of a h4 element."""
        self.assertEquals(sd(self.markdown), self.output)


class Heading5Tests(TestCase):
    """Tests the output of a h5 tag."""

    def setUp(self):
        self.output = '<h5>foo</h5>'
        self.markdown = '##### foo'

    def test_html(self):
        """Tests the HTML input of a h5 element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of a h5 element."""
        self.assertEquals(sd(self.markdown), self.output)


class ItalicTests(TestCase):
    """Tests the output of an italic element."""

    def setUp(self):
        self.output = '<p><i>foo</i></p>'

    def test_html(self):
        """Tests the HTML input of an italic element."""
        self.assertEquals(sd(self.output), self.output)


class ImageTests(TestCase):
    """Tests the output of an image element."""

    def setUp(self):
        self.output = '<p><img alt="bar" src="http://foo.com"></p>'
        self.markdown = '![bar](http://foo.com)'
        self.title_markdown = '![bar](http://foo.com "baz")'
        self.title_html =\
            '<p><img alt="bar" src="http://foo.com" title="baz"></p>'

    def test_html(self):
        """Tests the HTML input of an image element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of an image element."""
        self.assertEquals(sd(self.markdown), self.output)

    def test_title_attr_html(self):
        """Tests the HTML 'title' attribute of an image element."""
        self.assertEquals(sd(self.title_html), self.title_html)

    def test_title_attr_markdown(self):
        """Tests the Markdown 'title' attribute of an image element."""
        self.assertEquals(sd(self.title_markdown), self.title_html)


class InsertTests(TestCase):
    """Tests the output of an insert element."""

    def setUp(self):
        self.output = '<p><ins>foo</ins></p>'

    def test_html(self):
        """Tests the HTML input of an insert element."""
        self.assertEquals(sd(self.output), self.output)


class ListTests(TestCase):
    """Tests the output of a list element."""

    def setUp(self):
        self.unordered_markdown = '* foo'
        self.unordered_html = '<ul>\n<li>foo</li>\n</ul>'
        self.ordered_markdown = '1. foo'
        self.ordered_html = '<ol>\n<li>foo</li>\n</ol>'

    def test_unordered_markdown(self):
        """Tests the Markdown input of an unordered list element."""
        self.assertEquals(sd(self.unordered_markdown), self.unordered_html)

    def test_unordered_html(self):
        """Tests the HTML input of an unordered list element."""
        self.assertEquals(sd(self.unordered_html), self.unordered_html)

    def test_ordered_markdown(self):
        """Tests the Markdown input of an ordered list element."""
        self.assertEquals(sd(self.unordered_markdown), self.unordered_html)

    def test_ordered_html(self):
        """Tests the HTML input of an ordered list element."""
        self.assertEquals(sd(self.ordered_html), self.ordered_html)


class PreTests(TestCase):
    """Tests the output of a pre element."""

    def setUp(self):
        self.output = '<pre><code>foo\n</code></pre>'
        self.markdown1 = '```\nfoo\n```'
        self.markdown2 = '~~~\nfoo\n~~~'

    def test_html(self):
        """Tests the HTML input of a pre element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown1(self):
        """Tests the '```' Markdown input of a pre element."""
        self.assertEquals(sd(self.markdown1), self.output)

    def test_markdown2(self):
        """Tests the '~~~' Markdown input of a pre element."""
        self.assertEquals(sd(self.markdown2), self.output)


class StrongTests(TestCase):
    """Tests the output of a strong element."""

    def setUp(self):
        self.output = '<p><ins>foo</ins></p>'
        self.markdown = '**foo**'

    def test_html(self):
        """Tests the HTML input of an strong element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of an strong element."""
        self.assertEquals(sd(self.output), self.output)


class SubscriptTests(TestCase):
    """Tests the output of an subscript element."""

    def setUp(self):
        self.output = '<p><sub>foo</sub></p>'

    def test_html(self):
        """Tests the HTML input of an subscript element."""
        self.assertEquals(sd(self.output), self.output)


class SuperscriptTests(TestCase):
    """Tests the output of an superscript element."""

    def setUp(self):
        self.output = '<p><sup>foo</sup></p>'

    def test_html(self):
        """Tests the HTML input of an superscript element."""
        self.assertEquals(sd(self.output), self.output)


class TableTests(TestCase):
    """Tests the output of a table element."""
    def setUp(self):
        self.markdown = """
First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell
"""
        self.output = """\
<table>
<thead>
<tr>
<th>First Header</th>
<th>Second Header</th>
</tr>
</thead>
<tbody>
<tr>
<td>Content Cell</td>
<td>Content Cell</td>
</tr>
<tr>
<td>Content Cell</td>
<td>Content Cell</td>
</tr>
</tbody>
</table>\
"""

    def test_html(self):
        """Tests the HTML input of a table element."""
        self.assertEquals(sd(self.output), self.output)

    def test_markdown(self):
        """Tests the Markdown input of a table element."""
        self.assertEquals(sd(self.markdown), self.output)
