style = f"""
    <style>
    body, .stApp {{
        background: linear-gradient(rgba(40, 86, 207, 0.83), rgba(40, 86, 207, 0.83)), url('https://images.unsplash.com/photo-1519389950473-47ba0277781c');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .block-container {{
        padding-top: 1.2vw !important;
        padding-bottom: 0 !important;
        max-width: 100vw !important;
    }}
    .main-title {{
        color: white;
        font-size: 2.7em;
        font-weight: 800;
        text-align: center;
        margin: 2.2em 0 0.3em 0;
        letter-spacing: 1px;
    }}
    .main-subtitle {{
        color: #e9e8ff; font-size: 1.13em; text-align:center; font-weight: 300;
        max-width: 510px; margin: 0 auto 3em auto; line-height:1.5em;
    }}
    .marketplaces-title {{
        color: #fff; font-size: 1.38em; font-weight: 700; text-align:center; margin-bottom: 1.5em; margin-top: 0.9em; letter-spacing: .5px;
        text-shadow:0 1px 6px #2158b255;
    }}
    .markets-row {{
        display: flex; flex-direction: row; justify-content:center; align-items:center;
        gap: 2.5em; margin-top:0.7em;margin-bottom:3em;
    }}
    .market-ic-box svg {{filter: drop-shadow(0px 1px 9px #2d359933);}}
    .section-adv {{ margin: 2.6em 0 1.2em 0; }}
    .adv-title {{ color: white; font-size: 2.18em; font-weight: 800; text-align: center; margin-bottom: 0.7em; margin-top:1.7em; letter-spacing: .7px; }}
    .adv-text {{
        color: #e6edff; text-align: center; font-size: 1.11em; max-width: 830px; margin: 0 auto 2.18em auto; line-height:1.57em;
    }}
    .adv-row {{
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: stretch;
        gap: 2em;
        margin: 2.3em 0 0.9em 0;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-right: calc(-50vw + 50%);
        padding: 0; box-sizing: border-box;
    }}
    .adv-item {{
        display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
        background: rgba(255,255,255,0.14);
        border-radius: 12px;
        padding: 32px 18px 22px 18px;
        min-width:230px; max-width:320px;
        color: #fff; text-align:center; box-shadow: 0 6px 28px rgba(0,0,60, 0.16);
        font-size:1.02em;
        font-weight:400;
    }}
    .adv-item-title {{ font-weight: 700; font-size: 1.13em; margin: 10px 0 8px 0; }}
    .adv-item-desc {{ font-weight:300; font-size: 1.01em; }}
    @media (max-width: 980px) {{
        .adv-row {{ flex-direction: column !important; gap: 1.3em !important; width:100% !important; margin-left: 0 !important; margin-right:0!important; }}
        .adv-item {{min-width:200px}}
    }}
    </style>
"""