import streamlit as st


def show_about_me_sidebar():
    """Display compact about me information in sidebar footer"""
    st.markdown("""
    <style>
        .sidebar-footer {
            padding: 15px;
            margin-top: auto;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .footer-title {
            font-size: 1.1em;
            margin-bottom: 10px;
            color: white;
        }
        .footer-text {
            font-size: 0.85em;
            line-height: 1.4;
            color: rgba(255, 255, 255, 0.8);
        }
        .footer-link {
            color: #7bb1ff !important;
            text-decoration: none;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
        st.markdown('<div class="footer-title">👨🏻 About Developer</div>', unsafe_allow_html=True)

        # Use st.image() instead of HTML img tag
      

        st.markdown("""
        <div class="footer-text"> <strong>Name: Mohammed Habibul Bashar</strong> <br> 
                     Department: Software Engineering<br>University: Zhengzhou University<br>
                    📧Email: habibftc54@gmail.com

        <a href="https://github.com/Habibftc" target="_blank" class="footer-link">💻 GitHub</a> | 
        <a href="https://www.facebook.com/share/15gnYoxtgr/" target="_blank" class="footer-link">🔗 Facebook</a>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)