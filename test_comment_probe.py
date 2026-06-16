from pathlib import Path
import zipfile
from docx import Document
from comments import extract_comments, extract_body_text

path = Path('test_comments.docx')
if path.exists():
    path.unlink()

doc = Document()
doc.add_paragraph('Hello world')
doc.save(path)

with zipfile.ZipFile(path, 'a') as z:
    comments_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:comment w:id="0" w:author="Alice" w:date="2026-06-16T12:00:00Z">
    <w:p><w:r><w:t>This is a colleague comment.</w:t></w:r></w:p>
  </w:comment>
</w:comments>'''
    z.writestr('word/comments.xml', comments_xml)

print('zip names:')
with zipfile.ZipFile(path, 'r') as z:
    print(z.namelist())
    print('has comments.xml', 'word/comments.xml' in z.namelist())

print('extract_comments:', extract_comments(str(path)))
print('body:', extract_body_text(str(path)))
