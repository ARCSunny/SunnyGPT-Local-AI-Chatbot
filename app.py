import streamlit as st
import json
import uuid
from memory import ChatStore
from google import genai

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="SunnyGPT",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Gemini client via Streamlit Secrets
client = genai.Client(api_key=st.secrets.get("GEMINI_API_KEY", ""))
MODEL_NAME = "gemini-3.6-flash"
APP_NAME = "SunnyGPT"
APP_LOGO = "💬"
SUNNY_COLOR = "#3b82f6"  
GPT_COLOR = "#10b981"    

store = ChatStore()

# --------------------------------------------------------------------------
# Session state bootstrap
# --------------------------------------------------------------------------
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())

if "chat_pending_delete" not in st.session_state:
    st.session_state.chat_pending_delete = None

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# --------------------------------------------------------------------------
# Theme colors
# --------------------------------------------------------------------------
if st.session_state.theme == "dark":
    C = {
        "bg": "#212121",
        "sidebar_bg": "#171717",
        "border": "#2f2f2f",
        "text": "#ececec",
        "muted": "#8e8ea0",
        "hover": "#2b2b2b",
        "active": "#2f2f2f",
        "input_bg": "#2f2f2f",
        "input_text": "#ececec",
        "shadow": "rgba(0,0,0,0.35)",
    }
else:
    C = {
        "bg": "#ffffff",
        "sidebar_bg": "#f7f7f8",
        "border": "#d9d9e0",
        "text": "#0d0d0d",
        "muted": "#6e6e80",
        "hover": "#f0f0f2",
        "active": "#e9e9ec",
        "input_bg": "#ffffff",
        "input_text": "#0d0d0d",
        "shadow": "rgba(0,0,0,0.08)",
    }

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        section.main,
        .block-container {{
            background-color: {C['bg']} !important;
            color: {C['text']} !important;
        }}

        header[data-testid="stHeader"] {{
            background-color: {C['bg']} !important;
        }}
        [data-testid="stToolbarActions"],
        [data-testid="stStatusWidget"],
        #MainMenu,
        [data-testid="stDecoration"] {{
            display: none !important;
        }}

        html, body {{
            background-color: {C['bg']} !important;
        }}

        [data-testid="stBottom"],
        [data-testid="stBottom"] > div,
        [data-testid="stBottomBlockContainer"],
        [data-testid="stChatInputContainer"],
        div:has(> [data-testid="stChatInput"]) {{
            background-color: {C['bg']} !important;
            box-shadow: none !important;
            border: none !important;
        }}

        footer {{visibility: hidden;}}

        section[data-testid="stSidebar"] {{
            background-color: {C['sidebar_bg']} !important;
            border-right: 1px solid {C['border']};
        }}
        section[data-testid="stSidebar"] > div {{
            padding-top: 0.5rem;
            display: flex;
            flex-direction: column;
            height: 100%;
            background-color: {C['sidebar_bg']} !important;
        }}

        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {{
            opacity: 1 !important;
            visibility: visible !important;
            color: {C['text']} !important;
            background-color: {C['sidebar_bg']} !important;
            border: 1px solid {C['border']} !important;
            border-radius: 8px !important;
        }}
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg {{
            fill: {C['text']} !important;
        }}

        .brand-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 6px 4px 18px 4px;
        }}
        .brand-logo {{ font-size: 26px; line-height: 1; }}
        .brand-name {{ font-size: 20px; font-weight: 600; color: {C['text']}; }}

        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
            color: {C['muted']} !important;
        }}

        .side-label {{
            color: {C['muted']};
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin: 14px 4px 6px 4px;
        }}

        [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {{
            align-items: center !important;
            gap: 4px !important;
            margin-bottom: 4px !important;
        }}

        section[data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            height: 38px;
            text-align: left;
            background-color: {C['sidebar_bg']};
            color: {C['text']};
            border: 1px solid {C['border']};
            border-radius: 10px;
            padding: 6px 10px;
            font-size: 14px;
            box-shadow: 0 1px 2px {C['shadow']};
            transition: background-color 0.15s ease, border-color 0.15s ease;
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background-color: {C['hover']};
            border-color: {C['muted']};
        }}

        .active-chat > button {{
            background-color: {C['active']} !important;
            border-color: {C['muted']} !important;
        }}

        .delete-btn div[data-testid="stButton"] button {{
            width: 38px !important;
            min-width: 38px !important;
            height: 38px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            font-size: 14px !important;
            border: 1px solid {C['border']} !important;
            border-radius: 10px !important;
            background-color: {C['sidebar_bg']} !important;
            box-shadow: 0 1px 2px {C['shadow']};
        }}
        .delete-btn div[data-testid="stButton"] button:hover {{
            background-color: {C['hover']} !important;
            border-color: {C['muted']} !important;
        }}

        .block-container {{
            max-width: 780px;
            padding-top: 2rem;
            padding-bottom: 6rem;
        }}

        [data-testid="stChatMessage"] {{
            background-color: transparent;
            color: {C['text']};
        }}

        [data-testid="stChatInput"] {{
            background-color: transparent !important;
        }}
        [data-testid="stChatInput"] div {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stChatInput"] > div {{
            background-color: {C['input_bg']} !important;
            border: 1px solid {C['border']} !important;
            border-radius: 24px !important;
            box-shadow: 0 2px 8px {C['shadow']};
        }}
        [data-testid="stChatInput"] textarea {{
            background-color: transparent !important;
            color: {C['input_text']} !important;
            border: none !important;
            box-shadow: none !important;
            padding: 12px 48px 12px 16px !important;
        }}
        [data-testid="stChatInput"] textarea::placeholder {{
            color: {C['muted']} !important;
            opacity: 1 !important;
        }}
        [data-testid="stChatInput"] > div:focus-within {{
            border-color: {C['muted']} !important;
            box-shadow: 0 2px 10px {C['shadow']};
        }}
        [data-testid="stChatInput"] button {{
            background-color: {C['input_bg']} !important;
            border: none !important;
            border-radius: 50% !important;
            color: {C['input_text']} !important;
        }}

        .empty-title {{
            text-align: center;
            font-size: 32px;
            font-weight: 600;
            color: {C['text']};
            margin-top: 16vh;
        }}
        .empty-sub {{
            text-align: center;
            color: {C['muted']};
            font-size: 15px;
            margin-top: 6px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def clean_text(text: str) -> str:
    if not text:
        return text
    text = text.replace("\\n", "\n")
    text = text.replace("\\t", "\t")
    return text


def stream_response(history):
    contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
    
    try:
        response_stream = client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=contents
        )
        for chunk in response_stream:
            if chunk.text:
                yield clean_text(chunk.text)
    except Exception as e:
        yield f"⚠️ Error communicating with Gemini API: {e}"


def switch_chat(chat_id: str):
    st.session_state.current_chat_id = chat_id
    st.session_state.chat_pending_delete = None


def new_chat():
    st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chat_pending_delete = None


def delete_chat(chat_id: str):
    store.delete_chat(chat_id)
    if st.session_state.current_chat_id == chat_id:
        st.session_state.current_chat_id = str(uuid.uuid4())
    st.session_state.chat_pending_delete = None


def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div class="brand-row">
            <span class="brand-logo">{APP_LOGO}</span>
            <span class="brand-name">
                <span style="color: {SUNNY_COLOR};">Sunny</span><span style="color: {GPT_COLOR};">GPT</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("➕  New chat", key="new_chat_btn", use_container_width=True):
        new_chat()
        st.rerun()

    st.markdown('<div class="side-label">Chat history</div>', unsafe_allow_html=True)

    chats = store.all_chats()

    if not chats:
        st.caption("No conversations yet.")

    for chat in chats:
        is_active = chat["id"] == st.session_state.current_chat_id
        pending_delete = st.session_state.chat_pending_delete == chat["id"]

        col_title, col_del = st.columns([5, 1])

        with col_title:
            wrapper_class = "active-chat" if is_active else ""
            st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
            if st.button(chat["title"] or "New chat", key=f"open_{chat['id']}", use_container_width=True):
                switch_chat(chat["id"])
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with col_del:
            st.markdown('<div class="delete-btn">', unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{chat['id']}", use_container_width=True):
                st.session_state.chat_pending_delete = chat["id"]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        if pending_delete:
            st.warning(f"Delete “{chat['title']}”?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Delete", key=f"confirm_del_{chat['id']}", use_container_width=True):
                    delete_chat(chat["id"])
                    st.rerun()
            with c2:
                if st.button("Cancel", key=f"cancel_del_{chat['id']}", use_container_width=True):
                    st.session_state.chat_pending_delete = None
                    st.rerun()

    st.markdown("<div style='margin-top: auto;'></div>", unsafe_allow_html=True)
    st.markdown(f"<hr style='border-color: {C['border']}; margin: 10px 0;'>", unsafe_allow_html=True)
    theme_label = "☀️  Light mode" if st.session_state.theme == "dark" else "🌙  Dark mode"
    if st.button(theme_label, key="theme_toggle_btn", use_container_width=True):
        toggle_theme()
        st.rerun()

# --------------------------------------------------------------------------
# Main chat area
# --------------------------------------------------------------------------
current_chat = store.get(st.session_state.current_chat_id)
messages = current_chat["messages"] if current_chat else []

if not messages:
    st.markdown(
        f'<div class="empty-title">{APP_LOGO} <span style="color: {SUNNY_COLOR};">Sunny</span><span style="color: {GPT_COLOR};">GPT</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="empty-sub">Ask me anything to get started.</div>', unsafe_allow_html=True)
else:
    for msg in messages:
        avatar = "🧑" if msg["role"] == "user" else APP_LOGO
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

user_input = st.chat_input("What's on your mind?", submit_mode="stop")

if user_input:
    store.add_message(st.session_state.current_chat_id, "user", user_input)

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=APP_LOGO):
        placeholder = st.empty()
        response_text = ""

        history = store.get(st.session_state.current_chat_id)["messages"]

        for chunk in stream_response(history):
            response_text += chunk
            placeholder.markdown(response_text + "▌")

        placeholder.markdown(response_text)

    store.add_message(st.session_state.current_chat_id, "assistant", response_text)
    st.rerun()