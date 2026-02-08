"""
Message templates for notifications.
Provides formatted output for different notification channels.
"""
from datetime import datetime
from app.detection.base_detector import ChangeReport


def format_text_report(report: ChangeReport, source_name: str = None) -> str:
    """
    Format a plain text report for console/email.
    
    Args:
        report: The change report
        source_name: Optional source identifier
        
    Returns:
        Formatted plain text string
    """
    lines = []
    header = "Change Detection Report"
    if source_name:
        header += f" - {source_name}"
    
    lines.append("=" * 50)
    lines.append(header)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)
    
    if not report.has_changes:
        lines.append("\n✅ No changes detected.")
        return "\n".join(lines)
    
    lines.append(f"\n📊 Summary: {report.summary()}")
    lines.append("-" * 50)
    
    # New items
    if report.new_items:
        lines.append(f"\n🆕 NEW ITEMS ({len(report.new_items)}):")
        for item in report.new_items[:10]:
            display = " | ".join(f"{k}: {v}" for k, v in list(item.items())[:3])
            lines.append(f"  → {display}")
        if len(report.new_items) > 10:
            lines.append(f"  ... and {len(report.new_items) - 10} more")
    
    # Removed items
    if report.removed_items:
        lines.append(f"\n❌ REMOVED ITEMS ({len(report.removed_items)}):")
        for item in report.removed_items[:10]:
            display = " | ".join(f"{k}: {v}" for k, v in list(item.items())[:3])
            lines.append(f"  → {display}")
        if len(report.removed_items) > 10:
            lines.append(f"  ... and {len(report.removed_items) - 10} more")
    
    # Modified items
    if report.modified_items:
        lines.append(f"\n📝 MODIFIED ITEMS ({len(report.modified_items)}):")
        for change in report.modified_items[:10]:
            lines.append(f"  → {change.item_id}")
            for field, (old_val, new_val) in change.changed_fields.items():
                lines.append(f"      {field}: {old_val} → {new_val}")
        if len(report.modified_items) > 10:
            lines.append(f"  ... and {len(report.modified_items) - 10} more")
    
    return "\n".join(lines)


def format_html_report(report: ChangeReport, source_name: str = None) -> str:
    """
    Format an HTML report for email.
    
    Args:
        report: The change report
        source_name: Optional source identifier
        
    Returns:
        Formatted HTML string
    """
    header = "Change Detection Report"
    if source_name:
        header += f" - {source_name}"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #2c3e50; color: white; padding: 15px; border-radius: 5px; }}
            .summary {{ background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .section {{ margin: 15px 0; }}
            .new {{ color: #27ae60; }}
            .removed {{ color: #e74c3c; }}
            .modified {{ color: #f39c12; }}
            .item {{ background: #f9f9f9; padding: 8px; margin: 5px 0; border-left: 3px solid #3498db; }}
            .change {{ font-size: 0.9em; color: #666; margin-left: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>📊 {header}</h2>
            <small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
        </div>
    """
    
    if not report.has_changes:
        html += '<div class="summary">✅ No changes detected.</div>'
    else:
        html += f'<div class="summary"><strong>Summary:</strong> {report.summary()}</div>'
        
        # New items
        if report.new_items:
            html += f'<div class="section"><h3 class="new">🆕 New Items ({len(report.new_items)})</h3>'
            for item in report.new_items[:10]:
                display = " | ".join(f"{k}: {v}" for k, v in list(item.items())[:3])
                html += f'<div class="item">{display}</div>'
            if len(report.new_items) > 10:
                html += f'<p>... and {len(report.new_items) - 10} more</p>'
            html += '</div>'
        
        # Removed items
        if report.removed_items:
            html += f'<div class="section"><h3 class="removed">❌ Removed Items ({len(report.removed_items)})</h3>'
            for item in report.removed_items[:10]:
                display = " | ".join(f"{k}: {v}" for k, v in list(item.items())[:3])
                html += f'<div class="item">{display}</div>'
            if len(report.removed_items) > 10:
                html += f'<p>... and {len(report.removed_items) - 10} more</p>'
            html += '</div>'
        
        # Modified items
        if report.modified_items:
            html += f'<div class="section"><h3 class="modified">📝 Modified Items ({len(report.modified_items)})</h3>'
            for change in report.modified_items[:10]:
                html += f'<div class="item"><strong>{change.item_id}</strong>'
                for field, (old_val, new_val) in change.changed_fields.items():
                    html += f'<div class="change">{field}: <s>{old_val}</s> → <strong>{new_val}</strong></div>'
                html += '</div>'
            if len(report.modified_items) > 10:
                html += f'<p>... and {len(report.modified_items) - 10} more</p>'
            html += '</div>'
    
    html += '</body></html>'
    return html


def format_telegram_report(report: ChangeReport, source_name: str = None) -> str:
    """
    Format a Telegram-friendly report using Markdown.
    
    Args:
        report: The change report
        source_name: Optional source identifier
        
    Returns:
        Formatted Markdown string for Telegram
    """
    lines = []
    header = "📊 *Change Detection Report*"
    if source_name:
        header += f" \\- `{source_name}`"
    
    lines.append(header)
    lines.append(f"🕐 {datetime.now().strftime('%Y\\-%m\\-%d %H:%M')}")
    lines.append("")
    
    if not report.has_changes:
        lines.append("✅ No changes detected\\.")
        return "\n".join(lines)
    
    lines.append(f"*Summary:* {_escape_markdown(report.summary())}")
    lines.append("")
    
    # New items (compact)
    if report.new_items:
        lines.append(f"🆕 *New Items:* {len(report.new_items)}")
        for item in report.new_items[:5]:
            first_val = list(item.values())[0] if item else "Unknown"
            lines.append(f"  • {_escape_markdown(str(first_val)[:50])}")
        if len(report.new_items) > 5:
            lines.append(f"  _\\.\\.\\. and {len(report.new_items) - 5} more_")
    
    # Removed items (compact)
    if report.removed_items:
        lines.append(f"\n❌ *Removed:* {len(report.removed_items)}")
        for item in report.removed_items[:5]:
            first_val = list(item.values())[0] if item else "Unknown"
            lines.append(f"  • {_escape_markdown(str(first_val)[:50])}")
        if len(report.removed_items) > 5:
            lines.append(f"  _\\.\\.\\. and {len(report.removed_items) - 5} more_")
    
    # Modified items (compact)
    if report.modified_items:
        lines.append(f"\n📝 *Modified:* {len(report.modified_items)}")
        for change in report.modified_items[:5]:
            lines.append(f"  • {_escape_markdown(change.item_id[:40])}")
        if len(report.modified_items) > 5:
            lines.append(f"  _\\.\\.\\. and {len(report.modified_items) - 5} more_")
    
    return "\n".join(lines)


def _escape_markdown(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text
