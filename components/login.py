import streamlit as st
import json
import os
import bcrypt

USUARIOS_PATH = os.path.join(os.path.dirname(__file__), 'usuarios.json')

def cargar_usuarios():
    if not os.path.isfile(USUARIOS_PATH):
        return []
    with open(USUARIOS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def verificar_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

def login_form():
    # Ocultar sidebar y menú Streamlit en la pantalla de login
    # st.set_page_config(page_title="Login | Dashboard", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")  # ¡No llamar aquí!
    # --- BLOQUE CSS ÚNICO Y ULTRA-ESPECÍFICO PARA LOGIN Y BOTONES ---
    hide_streamlit_style = """
        <style>
        #MainMenu, footer, header, section[data-testid=\"stSidebar\"] {display: none !important;}
        html, body, .stApp {height: 100% !important;}
        .block-container {padding-top: 0 !important; height: 100vh !important; display: flex; align-items: center; justify-content: center;}
        .login-outer-flex {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            min-height: 100vh; width: 100vw; background: #f8fafc;
        }
        .login-main-container {
            width: 100%; max-width: 410px; height: 500px; min-height: 500px;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        .login-header {margin-bottom: 4px !important; padding: 0 !important;}
        .login-header h1 {margin: 0 0 4px 0 !important;}
        .login-form-block {width: 100%;}
        /* --- BOTONES LOGIN Y REGISTRO ULTRA-ESPECÍFICO --- */
        .login-form-buttons .stButton>button[data-testid="baseButton-login_btn_custom"],
        .login-form-buttons .stButton>button[data-testid="baseButton-registro_btn_custom"] {
            background: linear-gradient(90deg,#2563eb 0%,#00b4d8 100%) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 22px !important;
            font-weight: 800 !important;
            font-size: 1.13rem !important;
            padding: 0.7rem 2.1rem !important;
            min-width: 140px; max-width: 180px;
            box-shadow: 0 4px 24px #2563eb33, 0 1.5px 6px #00b4d822;
            letter-spacing: 0.5px;
            margin: 0 8px 0 0 !important;
            display: inline-block !important;
            text-align: center !important;
            transition: background 0.18s, color 0.18s, transform 0.13s cubic-bezier(.4,1.3,.6,1.0), box-shadow 0.18s;
            outline: none !important;
        }
        .login-form-buttons .stButton>button[data-testid="baseButton-login_btn_custom"]:hover,
        .login-form-buttons .stButton>button[data-testid="baseButton-registro_btn_custom"]:hover {
            background: linear-gradient(90deg,#00b4d8 0%,#2563eb 100%) !important;
            color: #fff !important;
            transform: scale(1.08);
            box-shadow: 0 8px 32px #2563eb55, 0 2px 12px #00b4d855;
        }
        .login-form-buttons-outer, .login-form-buttons {
            width: 100%; display: flex; justify-content: center; align-items: center; margin: 0; padding: 0;
        }
        .login-form-buttons {
            flex-direction: row; gap: 16px; width: auto; margin: 0 auto;
        }
        /* INPUTS compactos y centrados */
        .login-input input, .stTextInput input {
            border-radius: 7px !important;
            font-size: 0.98rem !important;
            padding: 0.22rem 0.5rem !important;
            color: #222 !important;
            background: #f8fafc !important;
            border: 1.5px solid #cbd5e1 !important;
            max-width: 300px !important;
            min-width: 180px !important;
            width: 100% !important;
            margin: 0 auto !important;
            display: block !important;
        }
        .stTextInput {max-width: 300px !important; margin-left: auto !important; margin-right: auto !important;}
        label, .stTextInput label {color: #222 !important; font-size: 0.97rem !important;}
        /* Bloque planes perfectamente centrado y compacto */
        .login-planes {
            margin-top: 8px !important;
            display: flex; flex-direction: row; align-items: flex-start; justify-content: center; gap: 16px;
            width: 100%; text-align: center;
        }
        .plan-card, .plan-card-pro {
            background: #fff; border-radius: 14px; box-shadow: 0 2px 12px #2563eb22;
            padding: 0.7rem 1.1rem 0.7rem 1.1rem; min-width: 140px; max-width: 180px; margin: 0;
            display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
        }
        </style>
    """
    # Si hay un import de estilos_dashboard, comentar o desactivar para login
    # import estilos_dashboard  # <-- Desactivar en login.py si existe
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.markdown("""
    <div class='login-outer-flex'>
      <div class='login-main-container'>
        <div class='login-header'>
            <!-- <div style='width:64px;height:64px;margin:0 auto 0.5rem auto;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#2563eb22 60%,#00b38622 100%);border-radius:50%;'>
                <span style='font-size:2.1rem;color:#2563eb;'>🚀</span>
            </div> -->
            <div style='width:64px;height:64px;margin:0 auto 0.5rem auto;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#2563eb22 60%,#00b38622 100%);border-radius:50%;'>
                <img src="/app/gpt/components/logo.png" alt="OptiCamp logo" style="width:54px;height:54px;object-fit:contain;display:block;margin:0 auto;" />
            </div>
            <h1 style='color:#2563eb;font-size:1.35rem;font-weight:800;margin:0 0 0.12rem 0;letter-spacing:-1px;'>OptiCamp</h1>
            <div style='color:#222;font-size:0.99rem;font-weight:500;max-width:340px;margin:0 auto 0.08rem auto;text-align:left;'>
                Hola,<br>
                <span style='color:#64748b;'>OptiCamp automatiza el análisis y gestión de campañas publicitarias. Sube tus datos o conecta tus cuentas y olvídate de hojas de cálculo.</span>
            </div>
        </div>
        <div class='login-form-block' style='margin-top:0.05rem;'>
    """, unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        st.markdown("""
        <label style='display:block;color:#222;font-weight:600;font-size:1.01rem;margin-bottom:0.18rem;text-align:center;'>Usuario</label>
        """, unsafe_allow_html=True)
        usuario = st.text_input("Usuario", key="login_usuario", placeholder="Usuario", help="Introduce tu usuario", label_visibility="collapsed")
        st.markdown("""
        <label style='display:block;color:#222;font-weight:600;font-size:1.01rem;margin-bottom:0.18rem;margin-top:0.5rem;text-align:center;'>Contraseña</label>
        """, unsafe_allow_html=True)
        password = st.text_input("Contraseña", type="password", key="login_password", placeholder="Contraseña", help="Introduce tu contraseña", label_visibility="collapsed")
        st.markdown("""
        <div class='login-form-buttons-outer'>
          <div class='login-form-buttons' style='width:100%;display:flex;justify-content:center;align-items:center;gap:16px;margin:0 auto;'>
        """, unsafe_allow_html=True)
        # Botones juntos y centrados, sin columnas
        login_btn = st.form_submit_button("Iniciar sesión")
        registro_btn = st.form_submit_button("Registro")
        st.markdown("""
          </div>
        </div>
        """, unsafe_allow_html=True)
        if login_btn:
            usuarios = cargar_usuarios()
            user = next((u for u in usuarios if u['usuario'] == usuario), None)
            if user and verificar_password(password, user['password_hash']):
                st.session_state['usuario_autenticado'] = True
                st.session_state['usuario_nombre'] = usuario
                st.session_state['usuario_plan'] = user.get('plan', 'BASIC')
                st.success(f"Acceso concedido. ¡Bienvenido, {usuario}! Plan: {st.session_state['usuario_plan']}")
                return
            else:
                st.error("Usuario o contraseña incorrectos.")
        if registro_btn:
            st.session_state['pantalla'] = 'registro'
            st.experimental_rerun()
    st.markdown("""
          </div>
          <div class='login-planes'>
            <div class='plan-card'>
                <div style='font-size:1.08rem;color:#2563eb;font-weight:700;margin-bottom:0.2rem;'>BASIC</div>
                <div style='font-size:1.25rem;font-weight:800;color:#111;margin-bottom:0.05rem;'>0€<span style='font-size:0.85rem;font-weight:500;color:#64748b;'>/mes</span></div>
                <ul style='text-align:left;font-size:0.93rem;color:#2563eb;margin:0 0 0.2rem 0;padding-left:0.7rem;'>
                  <li>✔️ Análisis campañas</li>
                  <li>✔️ Exportar informes</li>
                  <li>✔️ Recomendaciones</li>
                  <li>✔️ Simulador presupuesto</li>
                  <li>❌ Integración APIs</li>
                  <li>❌ Automatización</li>
                </ul>
                <div style='color:#64748b;font-size:0.88rem;'>Para freelance y pequeños negocios.</div>
            </div>
            <div class='plan-card-pro'>
                <div style='font-size:1.08rem;color:#2563eb;font-weight:700;margin-bottom:0.2rem;'>PRO</div>
                <div style='font-size:1.25rem;font-weight:800;color:#111;margin-bottom:0.05rem;'>29€<span style='font-size:0.85rem;font-weight:500;color:#64748b;'>/mes</span></div>
                <ul style='text-align:left;font-size:0.93rem;color:#2563eb;margin:0 0 0.2rem 0;padding-left:0.7rem;'>
                  <li>✔️ Todo lo de BASIC</li>
                  <li>✔️ Integración Google/Meta/TikTok</li>
                  <li>✔️ Automatización campañas</li>
                  <li>✔️ Reportes automáticos</li>
                  <li>✔️ Soporte prioritario</li>
                </ul>
                <div style='color:#64748b;font-size:0.88rem;'>Para agencias y usuarios avanzados.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
