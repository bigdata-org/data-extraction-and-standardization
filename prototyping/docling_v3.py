from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("test\\649af4f1-a280-43b3-8135-1664e7db178b.pdf")
with open('MarkItDown_Response.md', "w", encoding='utf-8') as f:
    f.write(result.text_content)
print(result.text_content)