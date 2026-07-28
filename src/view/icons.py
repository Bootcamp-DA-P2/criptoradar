"""
icons.py
========
Isotipos SVG que sustituyen a los emoticonos usados en CriptoRadar.

Un "isotipo" aquí es un símbolo gráfico minimalista (trazo simple, sin relleno
salvo excepciones puntuales) que hereda el color del texto mediante
`currentColor`, por lo que se adapta automáticamente a temas claros/oscuros.

Uso típico:

    from src.view.icons import icon_heading, icon_md, metric_html

    st.markdown(icon_heading("home", "CriptoRadar", level=1), unsafe_allow_html=True)
    st.markdown(icon_md("bar-chart", "**Dashboard Ejecutivo**"), unsafe_allow_html=True)
    st.markdown(metric_html("coin", "Precio actual", "$64,200.00", delta="+1.24%"), unsafe_allow_html=True)
"""

# ------------------------------------------------------------------
# 1. DEFINICIÓN DE ISOTIPOS (contenido interior de cada <svg>)
# ------------------------------------------------------------------
# viewBox común: 0 0 24 24

_ICONS = {

    "home": '<path d="M3 11.5 12 4l9 7.5" /><path d="M5.5 10v9.5h13V10" /><path d="M9.5 19.5V14h5v5.5" />',

    "bar-chart": '<rect x="4" y="12" width="3.6" height="8" rx="0.6" />'
                 '<rect x="10.2" y="7" width="3.6" height="13" rx="0.6" />'
                 '<rect x="16.4" y="3.5" width="3.6" height="16.5" rx="0.6" />',

    "coin": '<circle cx="12" cy="12" r="8.3" />'
            '<circle cx="12" cy="12" r="5.2" />'
            '<path d="M12 9v6M10.3 10.2h2.3a1.5 1.5 0 0 1 0 3h-2.6" />',

    "shield": '<path d="M12 3.3 19 6v5.4c0 5-3 8.2-7 9.3-4-1.1-7-4.3-7-9.3V6z" />'
              '<path d="M9 12l2 2 4-4.2" />',

    "alert": '<path d="M12 3.6 21 19H3z" />'
             '<path d="M12 9.6v4.6" />'
             '<circle cx="12" cy="16.9" r="0.9" fill="currentColor" stroke="none" />',

    "tool": '<path d="M14.7 6.3a3.7 3.7 0 0 0 5 5L15 16l-3-3-6.6 6.6-2-2L10 10.3 7 7.3a3.7 3.7 0 0 0 5-5l2 2z" />'
            '<path d="M5 19l0 0" />',

    "book": '<path d="M4 5.2C6 4 9 4 11.5 5.4V19c-2.5-1.4-5.5-1.4-7.5-.2z" />'
            '<path d="M20 5.2C18 4 15 4 12.5 5.4V19c2.5-1.4 5.5-1.4 7.5-.2z" />',

    "trending-up": '<path d="M3.5 16.5 9.5 10l4 4 6.5-7.5" />'
                   '<path d="M15.5 6h4.5v4.5" />',

    "trending-down": '<path d="M3.5 7.5 9.5 14l4-4 6.5 7.5" />'
                     '<path d="M15.5 18h4.5v-4.5" />',

    "banknote": '<rect x="2.7" y="6.5" width="18.6" height="11" rx="1.4" />'
                '<circle cx="12" cy="12" r="2.6" />'
                '<path d="M5.2 9v0M18.8 15v0" stroke-width="2.4" stroke-linecap="round" />',

    "target": '<circle cx="12" cy="12" r="8.3" />'
              '<circle cx="12" cy="12" r="4.6" />'
              '<circle cx="12" cy="12" r="0.9" fill="currentColor" stroke="none" />',

    "search": '<circle cx="10.8" cy="10.8" r="6.3" />'
              '<path d="M15.5 15.5 20.5 20.5" />',

    "trophy": '<path d="M7 4h10v5.2A5 5 0 0 1 12 14.2 5 5 0 0 1 7 9.2Z" />'
              '<path d="M7 6H4.3C4 8.6 5.6 10.6 7.8 11" />'
              '<path d="M17 6h2.7c0.3 2.6-1.3 4.6-3.5 5" />'
              '<path d="M12 14.2V17.5" /><path d="M8.5 20.5h7l-1-3h-5z" />',

    "pin": '<path d="M12 21s6.5-6.1 6.5-11.2A6.5 6.5 0 0 0 5.5 9.8C5.5 14.9 12 21 12 21z" />'
           '<circle cx="12" cy="9.6" r="2.3" />',

    "document": '<path d="M6.5 3h8l3 3v15h-11z" />'
                '<path d="M14.5 3v3h3" />'
                '<path d="M9 12h6M9 15.3h6M9 8.7h2.5" />',

    "settings": '<circle cx="12" cy="12" r="3" />'
                '<path d="M12 3.3v2.4M12 18.3v2.4M4.6 7.2l2.1 1.2M17.3 15.6l2.1 1.2'
                'M4.6 16.8l2.1-1.2M17.3 8.4l2.1-1.2M3.3 12h2.4M18.3 12h2.4" />',

    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="1.6" />'
                '<path d="M3.5 9.6h17M8 3v4M16 3v4" />',

    "clock": '<circle cx="12" cy="12" r="8.3" />'
             '<path d="M12 7.5V12l3.2 2" />',

    "link": '<path d="M9.5 14.5 14.5 9.5" />'
            '<path d="M8 16.2 5.6 13.8a4 4 0 0 1 0-5.6l2-2a4 4 0 0 1 5.6 0" />'
            '<path d="M16 7.8l2.4 2.4a4 4 0 0 1 0 5.6l-2 2a4 4 0 0 1-5.6 0" />',

    "check-circle": '<circle cx="12" cy="12" r="8.3" />'
                    '<path d="M8 12.3 11 15.3 16.3 9" />',

    "check": '<path d="M4.5 12.5 9.5 17.5 19.5 6.5" />',

    "user": '<circle cx="12" cy="8.6" r="3.6" />'
            '<path d="M4.8 20c1-3.7 4-5.6 7.2-5.6s6.2 1.9 7.2 5.6" />',

    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="1.6" />'
            '<path d="M3.5 6.5 12 13 20.5 6.5" />',

    "briefcase": '<rect x="3" y="7.5" width="18" height="12" rx="1.6" />'
                 '<path d="M8.5 7.5V5.8c0-.7.6-1.3 1.3-1.3h4.4c.7 0 1.3.6 1.3 1.3V7.5" />'
                 '<path d="M3 12.5h18" />',

    "laptop": '<rect x="4" y="4.5" width="16" height="10.5" rx="1.2" />'
              '<path d="M2.3 19h19.4" />',

    "database": '<ellipse cx="12" cy="6" rx="7.2" ry="2.8" />'
                '<path d="M4.8 6v12c0 1.5 3.2 2.8 7.2 2.8s7.2-1.3 7.2-2.8V6" />'
                '<path d="M4.8 12c0 1.5 3.2 2.8 7.2 2.8s7.2-1.3 7.2-2.8" />',

    "globe": '<circle cx="12" cy="12" r="8.3" />'
             '<path d="M3.7 12h16.6M12 3.7c2.6 2.4 4 5.3 4 8.3s-1.4 5.9-4 8.3c-2.6-2.4-4-5.3-4-8.3s1.4-5.9 4-8.3z" />',

    "cloud": '<path d="M7 18.5a4 4 0 0 1-.6-7.9 5.4 5.4 0 0 1 10.4-1.6A4.3 4.3 0 0 1 17 18.5z" />',

    "dot": '<circle cx="12" cy="12" r="6.5" fill="currentColor" stroke="none" />',

    "book-open": '<path d="M12 6.3C10 5 6.8 4.8 4 5.8v13c2.8-1 6 -0.8 8 0.5' \
                 'c2-1.3 5.2-1.5 8-0.5v-13c-2.8-1-6-0.8-8 0.5z" />'
                 '<path d="M12 6.3v13" />',
}

# Colores por defecto para los "semáforos" de estado (antes 🔴🟡🟢)
_DOT_COLORS = {
    "dot-green": "#2ecc71",
    "dot-yellow": "#f1c40f",
    "dot-red": "#e74c3c",
}


def icon(name: str, size: int = 20, color: str = "currentColor", stroke_width: float = 1.8) -> str:
    """Devuelve el marcado <svg> en línea para el isotipo `name`."""

    if name in _DOT_COLORS:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'width="{size}" height="{size}" style="vertical-align:-0.15em">'
            f'<circle cx="12" cy="12" r="7.5" fill="{_DOT_COLORS[name]}" /></svg>'
        )

    inner = _ICONS.get(name, _ICONS["dot"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'width="{size}" height="{size}" fill="none" stroke="{color}" '
        f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:-0.2em">{inner}</svg>'
    )


# ------------------------------------------------------------------
# 2. HELPERS DE COMPOSICIÓN (para usar con st.markdown(..., unsafe_allow_html=True))
# ------------------------------------------------------------------

def icon_heading(name: str, text: str, level: int = 1, size: int | None = None, color: str = "currentColor") -> str:
    """Título tipo st.title / st.header / st.subheader con isotipo SVG delante."""

    tag = f"h{max(1, min(level, 6))}"
    px = size or {1: 30, 2: 24, 3: 20}.get(level, 20)
    ico = icon(name, size=px, color=color)
    return (
        f'<{tag} style="display:flex;align-items:center;gap:0.45em;margin:0.2em 0;">'
        f'{ico}<span>{text}</span></{tag}>'
    )


def icon_md(name: str, text: str, size: int = 18, color: str = "currentColor") -> str:
    """Texto en línea (para reemplazar 'markdown' del tipo '📊 Texto')."""

    ico = icon(name, size=size, color=color)
    return f'<span style="display:inline-flex;align-items:center;gap:0.4em;">{ico}<span>{text}</span></span>'


def icon_box(name: str, text_md: str, kind: str = "info") -> str:
    """
    Caja de aviso equivalente a st.info/success/warning/error pero con
    isotipo SVG en la cabecera. `text_md` acepta saltos de línea '\\n'.
    """

    palette = {
        "info":    ("#1c3a5e", "#7ec8ff"),
        "success": ("#173d2e", "#7be3a6"),
        "warning": ("#4a3a12", "#ffcf6b"),
        "error":   ("#4a1e1e", "#ff8f8f"),
    }
    bg, border = palette.get(kind, palette["info"])
    ico = icon(name, size=20, color=border)
    body = text_md.replace("\n", "<br>")
    return (
        f'<div style="background:{bg};border-left:4px solid {border};'
        f'border-radius:6px;padding:0.9em 1.1em;margin:0.6em 0;">'
        f'<div style="display:flex;gap:0.5em;align-items:flex-start;">'
        f'{ico}<div>{body}</div></div></div>'
    )


def metric_html(name: str, label: str, value: str, delta: str | None = None) -> str:
    """Tarjeta equivalente a st.metric pero con isotipo SVG en vez de emoji."""

    ico = icon(name, size=18)
    delta_html = ""
    if delta is not None:
        positivo = not str(delta).strip().startswith("-")
        color = "#2ecc71" if positivo else "#e74c3c"
        signo = "▲" if positivo else "▼"
        delta_html = f'<div style="color:{color};font-size:0.85em;margin-top:2px;">{signo} {delta}</div>'

    return (
        '<div style="padding:0.4em 0;">'
        f'<div style="display:flex;align-items:center;gap:0.4em;color:#9aa4b2;font-size:0.85em;">'
        f'{ico}<span>{label}</span></div>'
        f'<div style="font-size:1.6em;font-weight:600;line-height:1.3;">{value}</div>'
        f'{delta_html}</div>'
    )
