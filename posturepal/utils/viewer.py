from streamlit.components.v1 import html

def render_model(model_path):
    html(f"""
    <model-viewer src="{model_path}"
                  alt="Posture Avatar"
                  auto-rotate
                  camera-controls
                  style="width: 100%; height: 600px; background-color: #1e1e1e;">
    </model-viewer>
    """, height=600)
