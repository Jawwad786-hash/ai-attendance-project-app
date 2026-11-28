import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    progress_html = ""
    if stats:
        stats_lookup = {label.lower(): value for _icon, label, value in stats}
        total = stats_lookup.get("total")
        attended = stats_lookup.get("attended")
        if isinstance(total, (int, float)) and isinstance(attended, (int, float)) and total > 0:
            pct = max(0, min(100, round((attended / total) * 100)))
            progress_html = (
                f'<div class="snap-progress-wrap">'
                f'<div class="snap-progress-meta"><span>Attendance</span><span>{pct}%</span></div>'
                f'<div class="snap-progress-track"><div class="snap-progress-fill" style="width:{pct}%;"></div></div>'
                f"</div>"
            )

    html = (
        f'<div class="snap-subject-card">'
        f'<div class="snap-subject-header">'
        f'<h3 class="snap-subject-title">{name}</h3>'
        f'<span class="snap-code-pill">{code}</span>'
        f"</div>"
        f'<p class="snap-subject-section">Section <strong style="color:#334155;">{section}</strong></p>'
    )

    if stats:
        html += '<div class="snap-chips-row">'
        for icon, label, value in stats:
            html += (
                f'<div class="snap-chip">'
                f'{icon} <strong style="color:#0F172A;">{value}</strong> {label}'
                f"</div>"
            )
        html += "</div>"

    html += f"{progress_html}</div>"
    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
