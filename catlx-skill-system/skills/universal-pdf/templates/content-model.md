# `pdf-create` content & options model

`create_pdf(opts, content)` takes two structures.

## `opts` (page/document options)
```jsonc
{
  "output": "report.pdf",              // required output path
  "page_size": "a4",                   // a4 | letter | legal | a3 | a5
  "margins": {"left":0.9,"right":0.9,"top":0.9,"bottom":0.9}, // inches
  "orientation": "portrait",           // (derived from page_size unless changed)
  "header": "Running header text",
  "footer": "Running footer text",
  "page_numbers": true,
  "metadata": {"title":"...","author":"...","subject":"...","keywords":"..."}
}
```
`create_from_markdown / create_from_text / create_from_html /
create_from_images` accept `opts` the same way and build `content` for you.

## `content` (ordered list of flowable dicts)
| type | fields | notes |
|---|---|---|
| `cover` | title, subtitle, author, date, organization | full title page |
| `heading` | text, level(1..4) | becomes a PDF bookmark too |
| `para` | text | supports `**bold**` `*italic*` `` `code` `` |
| `parahtml` | html | pass raw reportlab markup |
| `list` | items[], ordered(bool) | bullet or numbered |
| `table` | rows[][] , caption | first row is a styled header |
| `image` | path, width(pts), caption | vector raster fitted |
| `link` | text, url | hyperlink paragraph |
| `hr` | — | horizontal rule |
| `spacer` | height | vertical gap |
| `pagebreak` | — | force a new page |

Example:
```json
[
  {"type":"cover","title":"Q3 Report","subtitle":"FY26","author":"Finance","date":"2026-09-06"},
  {"type":"heading","text":"Executive summary","level":1},
  {"type":"para","text":"Strong growth in **North** and *APAC*."},
  {"type":"table","rows":[["Region","Growth"],["North","12%"],["APAC","18%"]],"caption":"Table 1"},
  {"type":"pagebreak"},
  {"type":"heading","text":"Details","level":1}
]
```
