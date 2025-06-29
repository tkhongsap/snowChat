import html
import re

import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler

image_url = f"{st.secrets['SUPABASE_STORAGE_URL']}/storage/v1/object/public/snowchat/"
gemini_url = image_url + "google-gemini-icon.png?t=2024-05-07T21%3A17%3A52.235Z"
mistral_url = (
    image_url
    + "mistral-ai-icon-logo-B3319DCA6B-seeklogo.com.png?t=2024-05-07T21%3A18%3A22.737Z"
)
openai_url = (
    image_url
    + "png-transparent-openai-chatgpt-logo-thumbnail.png?t=2024-05-07T21%3A18%3A44.079Z"
)
user_url = image_url + "cat-with-sunglasses.png?t=2024-05-07T21%3A17%3A21.951Z"
claude_url = image_url + "Claude.png?t=2024-05-07T21%3A16%3A17.252Z"
meta_url = image_url + "meta-logo.webp?t=2024-05-07T21%3A18%3A12.286Z"
snow_url = image_url + "Snowflake_idCkdSg0B6_6.png?t=2024-05-07T21%3A24%3A02.597Z"
qwen_url = image_url + "qwen.png?t=2024-06-07T08%3A51%3A36.363Z"
deepseek_url = image_url + "/deepseek-color.png"
grok_url = image_url + "/xAI-logo.jpg"

def get_model_url(model_name):
    if "qwen" in model_name.lower():
        return qwen_url
    elif "claude" in model_name.lower():
        return claude_url
    elif "llama" in model_name.lower():
        return meta_url
    elif "gemma" in model_name.lower():
        return gemini_url
    elif "arctic" in model_name.lower():
        return snow_url
    elif "gpt" in model_name.lower() or "o3" in model_name.lower():
        return openai_url
    elif "gemini" in model_name.lower():
        return gemini_url
    elif "deepseek" in model_name.lower():
        return deepseek_url
    elif "grok" in model_name.lower():
        return grok_url
    return mistral_url


def format_message(text):
    """
    This function is used to format the messages in the chatbot UI.

    Parameters:
    text (str): The text to be formatted.
    """
    text_blocks = re.split(r"```[\s\S]*?```", text)
    code_blocks = re.findall(r"```([\s\S]*?)```", text)

    text_blocks = [html.escape(block) for block in text_blocks]

    formatted_text = ""
    for i in range(len(text_blocks)):
        formatted_text += text_blocks[i].replace("\n", "<br>")
        if i < len(code_blocks):
            formatted_text += f'<pre style="white-space: pre-wrap; word-wrap: break-word;"><code>{html.escape(code_blocks[i])}</code></pre>'

    return formatted_text


def message_func(text, is_user=False, is_df=False, model="gpt"):
    """
    This function displays messages in the chatbot UI, ensuring proper alignment and avatar positioning.

    Parameters:
    text (str): The text to be displayed.
    is_user (bool): Whether the message is from the user or not.
    is_df (bool): Whether the message is a dataframe or not.
    """
    model_url = get_model_url(model)
    avatar_url = user_url if is_user else model_url
    message_bg_color = (
        "linear-gradient(135deg, #00B2FF 0%, #006AFF 100%)" if is_user else "#71797E"
    )
    avatar_class = "user-avatar" if is_user else "bot-avatar"
    alignment = "flex-end" if is_user else "flex-start"
    margin_side = "margin-left" if is_user else "margin-right"
    message_text = html.escape(text.strip()).replace('\n', '<br>')

    if message_text:  # Check if message_text is not empty
        if is_user:
            container_html = f"""
            <div style="display:flex; align-items:flex-start; justify-content:flex-end; margin:0; padding:0; margin-bottom:10px;">
                <div style="background:{message_bg_color}; color:white; border-radius:20px; padding:10px; margin-right:5px; max-width:75%; font-size:14px; margin:0; line-height:1.2; word-wrap:break-word;">
                    {message_text}
                </div>
                <img src="{avatar_url}" class="{avatar_class}" alt="avatar" style="width:40px; height:40px; margin:0;" />
            </div>
            """
        else:
            container_html = f"""
            <div style="display:flex; align-items:flex-start; justify-content:flex-start; margin:0; padding:0; margin-bottom:10px;">
                <img src="{avatar_url}" class="{avatar_class}" alt="avatar" style="width:30px; height:30px; margin:0; margin-right:5px; margin-top:5px;" />
                <div style="background:{message_bg_color}; color:white; border-radius:20px; padding:10px; margin-left:5px; max-width:75%; font-size:14px; margin:0; line-height:1.2; word-wrap:break-word;">
                    {message_text}
                </div>
            </div>
            """
        st.write(container_html, unsafe_allow_html=True)



class StreamlitUICallbackHandler(BaseCallbackHandler):
    def __init__(self, model):
        self.token_buffer = []
        self.placeholder = st.empty()
        self.has_streaming_ended = False
        self.has_streaming_started = False
        self.model = model
        self.avatar_url = get_model_url(model)
        self.final_message = ""

    def start_loading_message(self):
        loading_message_content = self._get_bot_message_container("Thinking...")
        self.placeholder.markdown(loading_message_content, unsafe_allow_html=True)

    def on_llm_new_token(self, token, run_id, parent_run_id=None, **kwargs):
        if not self.has_streaming_started:
            self.has_streaming_started = True

        self.token_buffer.append(token)
        complete_message = "".join(self.token_buffer)
        container_content = self._get_bot_message_container(complete_message)
        self.placeholder.markdown(container_content, unsafe_allow_html=True)
        self.final_message = "".join(self.token_buffer)

    def on_llm_end(self, response, run_id, parent_run_id=None, **kwargs):
        self.token_buffer = []
        self.has_streaming_ended = True
        self.has_streaming_started = False

    def _get_bot_message_container(self, text):
        """Generate the bot's message container style for the given text."""
        formatted_text = format_message(text.strip())
        if not formatted_text:  # If no formatted text, show "Thinking..."
            formatted_text = "Thinking..."
        container_content = f"""
        <div style="display:flex; align-items:flex-start; justify-content:flex-start; margin:0; padding:0;">
            <img src="{self.avatar_url}" class="bot-avatar" alt="avatar" style="width:30px; height:30px; margin:0;" />
            <div style="background:#71797E; color:white; border-radius:20px; padding:10px; margin-left:5px; max-width:75%; font-size:14px; line-height:1.2; word-wrap:break-word;">
                {formatted_text}
            </div>
        </div>
        """
        return container_content

    def display_dataframe(self, df):
        """
        Display the dataframe in Streamlit UI within the chat container.
        """
        message_alignment = "flex-start"
        avatar_class = "bot-avatar"

        st.write(
            f"""
            <div style="display: flex; align-items: flex-start; margin-bottom: 10px; justify-content: {message_alignment};">
                <img src="{self.avatar_url}" class="{avatar_class}" alt="avatar" style="width: 30px; height: 30px; margin-top: 0;" />
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(df)


    def __call__(self, *args, **kwargs):
        pass
