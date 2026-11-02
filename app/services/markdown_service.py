"""
Markdown 导出业务层

作用：把笔记数据转换成 Markdown 文本，方便前端下载/展示读书报告。
"""
from app.schemas.export import ExportNote

# 笔记类型显示文案
NOTE_TYPE_LABELS = {
    "highlight": "划线",
    "note": "笔记",
    "annotation": "批注",
    "划线": "划线",
    "笔记": "笔记",
    "批注": "批注",
}


def notes_to_markdown(title: str, notes: list[ExportNote]) -> str:
    """把笔记列表整理成按书名分组的 Markdown 文本。"""
    lines: list[str] = [f"# {title}", ""]

    # 按书名分组，让报告更清晰
    grouped: dict[str, list[ExportNote]] = {}
    for note in notes:
        grouped.setdefault(note.book_title, []).append(note)

    for book_title, book_notes in grouped.items():
        lines.append(f"## 《{book_title}》")
        lines.append("")
        for note in book_notes:
            note_type = NOTE_TYPE_LABELS.get(note.note_type, note.note_type)
            heading = note.chapter or note_type
            meta_parts = [f"类型：{note_type}"]
            if note.chapter:
                meta_parts.append(f"章节：{note.chapter}")
            if note.created_time:
                meta_parts.append(f"时间：{note.created_time}")
            lines.append(f"### {heading}")
            lines.append("")
            lines.append(f"**{' | '.join(meta_parts)}**")
            lines.append("")
            lines.append("> " + note.content.replace("\n", "\n> "))
            lines.append("")

    # 如果一条笔记都没有，输出空提示
    if not grouped:
        lines.append("暂无笔记数据。")
        lines.append("")

    return "\n".join(lines)
