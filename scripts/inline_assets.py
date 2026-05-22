#!/usr/bin/env python3
"""Inline external assets into HTML for self-contained use."""

# Read Chart.js
with open('C:/Users/user/AppData/Local/Temp/chart.min.js', 'r', encoding='utf-8') as f:
    chart_js = f.read()

# Read HTML
with open('data/marathon_anomaly_report.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace CDN script tag with inline script
cdn_tag = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'
inline_tag = f'<script>\n{chart_js}\n</script>\n'
html = html.replace(cdn_tag, inline_tag)

# Remove annotation plugin
annotation_tag = '<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>'
html = html.replace(annotation_tag, '')

# Save
with open('data/marathon_anomaly_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Verify
import re
external_links = re.findall(r'(?:src|href)="https?://', html)
print(f"外部依赖数量: {len(external_links)}")
print(f"文件大小: {len(html)/1024:.1f} KB")
print("HTML已完全封装，可离线使用！")