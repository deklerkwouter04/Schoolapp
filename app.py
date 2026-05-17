import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime
import graphviz

# ==========================================
# 1. OPSTELLING & STYL
# ==========================================
st.set_page_config(page_title="Akademie-Kampioen", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .hoof-kaart {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        padding: 40px;
        border-radius: 20px;
        border: 2px solid #3e3e5e;
        text-align: center;
        font-size: 28px;
        margin-bottom: 20px;
    }
    .wetenskap-teks { color: #00FFC8; font-family: 'Courier New', monospace; }
    
    /* Flip Card CSS wat inpas by die nuwe tema */
    .flip-card { background-color: transparent; width: 300px; height: 150px; perspective: 1000px; margin: auto;}
    .flip-card-inner { position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.6s; transform-style: preserve-3d; }
    .flip-card.flip .flip-card-inner { transform: rotateY(180deg); }
    .flip-card-front, .flip-card-back { position: absolute; width: 100%; height: 100%; -webkit-backface-visibility: hidden; backface-visibility: hidden; display: flex; align-items: center; justify-content: center; border: 2px solid #3e3e5e; background-color: #1e1e2f; border-radius: 10px;}
    
    /* Rooi flits-animasie vir die agterkant as die tyd om is */
    .flip-card-back { 
        transform: rotateY(180deg); 
        color: #ff4b4b; 
        font-size: 24px; 
        font-weight: bold;
    }
    
    .flits-aktief {
        animation: flits 0.75s ease-in-out 2;
    }
    
    @keyframes flits {
        0%, 100% { background-color: #1e1e2f; }
        50% { background-color: #ff4b4b; color: white; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. NO-SQL DATABASE LOGIC (JSON)
# ==========================================
DB_FILE = "db.json"

def init_db():
    if not os.path.exists(DB_FILE):
        db = {"users": {}, "leaderboard": [], "stats": []}
        with open(DB_FILE, "w") as f:
            json.dump(db, f)

def load_db():
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f)

init_db()

def opdateer_leerder_data_in_db():
    if st.session_state.user and st.session_state.user.get("role") != "admin":
        db = load_db()
        uid = st.session_state.user["id"]
        if uid in db["users"]:
            st.session_state.max_level = max(st.session_state.get("max_level", 1), st.session_state.level)
            
            db["users"][uid]["score"] = st.session_state.score
            db["users"][uid]["level"] = st.session_state.level
            db["users"][uid]["max_level"] = st.session_state.max_level
            save_db(db)
            
            st.session_state.user["score"] = st.session_state.score
            st.session_state.user["level"] = st.session_state.level
            st.session_state.user["max_level"] = st.session_state.max_level

# ==========================================
# 3. AUTHENTICATION & SESSION STATE
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None
if "level" not in st.session_state:
    st.session_state.level = 1
if "max_level" not in st.session_state:
    st.session_state.max_level = 1
if "score" not in st.session_state:
    st.session_state.score = 0
if "playing" not in st.session_state:
    st.session_state.playing = False

def login_flow():
    db = load_db()
    
    query_params = st.query_params
    if "user_id" in query_params:
        uid = query_params["user_id"]
        if uid in db["users"]:
            st.session_state.user = db["users"][uid]
            st.session_state.score = db["users"][uid].get("score", 0)
            st.session_state.level = db["users"][uid].get("level", 1)
            st.session_state.max_level = db["users"][uid].get("max_level", db["users"][uid].get("level", 1))
            st.success(f"Auto-aangeteken as {st.session_state.user['name']}!")
            time.sleep(1)
            st.rerun()

    st.markdown('<div class="hoof-kaart">🏆 Welkom by <span class="wetenskap-teks">Akademie-Kampioen</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Teken In", "Registreer", "Onderwyser/Cheatsheet"])
    
    with tab1:
        login_user = st.text_input("Gebruikersnaam")
        login_pass = st.text_input("Wagwoord", type="password")
        if st.button("Teken In"):
            for uid, udata in db["users"].items():
                if udata["name"] == login_user and udata["password"] == login_pass:
                    st.session_state.user = udata
                    st.session_state.score = udata.get("score", 0)
                    st.session_state.level = udata.get("level", 1)
                    st.session_state.max_level = udata.get("max_level", udata.get("level", 1))
                    st.rerun()
            st.error("Verkeerde besonderhede!")

    with tab2:
        reg_name = st.text_input("Nuwe Gebruikersnaam")
        reg_pass = st.text_input("Nuwe Wagwoord", type="password")
        reg_avatar = st.selectbox("Kies Avatar", ["👽 Alien", "🤖 Robot", "🧙 Towenaar", "🥷 Ninja"])
        if st.button("Registreer Nou"):
            new_id = str(len(db["users"]) + 1)
            db["users"][new_id] = {"id": new_id, "name": reg_name, "password": reg_pass, "avatar": reg_avatar, "level": 1, "max_level": 1, "score": 0}
            save_db(db)
            st.success(f"Geregistreer! Jou QR skakel is: `?user_id={new_id}`")

    with tab3:
        st.subheader("Cheatsheet & Video vir Studente")
        st.info("Hoe om in te teken:\n1. Skandeer die QR kode.\n2. Of tik jou naam en wagwoord in.\n3. Kies 'n vak in die spyskaart links.")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
        st.markdown("---")
        if st.text_input("Onderwyser Kode", type="password") == "admin123":
            st.session_state.user = {"name": "Onderwyser", "role": "admin"}
            st.rerun()

# ==========================================
# 4. EFFECTS & COMPONENTS (VOLSKERM MATRIX FIX)
# ==========================================
def run_matrix_transition(volgende_vlak):
    """Hierdie funksie spuit die Matrix-kode direk in die hoofskerm in om die hele bladsy te oorneem."""
    matrix_js = f"""
    <img src="void" style="display:none;" onerror="
        (function() {{
            if (document.getElementById('matrix-overlay')) return;
            var canvas = document.createElement('canvas');
            canvas.id = 'matrix-overlay';
            canvas.style.position = 'fixed';
            canvas.style.top = '0';
            canvas.style.left = '0';
            canvas.style.width = '100vw';
            canvas.style.height = '100vh';
            canvas.style.zIndex = '999999';
            canvas.style.background = 'black';
            document.body.appendChild(canvas);
            
            var ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            var chars = '01ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
            var drops = [];
            for(var x = 0; x < canvas.width/20; x++) drops[x] = 1;
            
            var inter = setInterval(function() {{
                ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#00FFC8';
                ctx.font = '20px monospace';
                for(var i = 0; i < drops.length; i++) {{
                    var text = chars[Math.floor(Math.random() * chars.length)];
                    ctx.fillText(text, i * 20, drops[i] * 20);
                    if(drops[i] * 20 > canvas.height && Math.random() > 0.975) drops[i] = 0;
                    drops[i]++;
                }}
                ctx.fillStyle = '#00FFC8';
                ctx.font = 'bold 40px monospace';
                ctx.textAlign = 'center';
                ctx.fillText('STELSEL OPGRADEER...', canvas.width / 2, canvas.height / 2 - 40);
                ctx.fillText('ONTSLUIT: VLAK {volgende_vlak}', canvas.width / 2, canvas.height / 2 + 30);
            }}, 33);
            
            setTimeout(function() {{
                clearInterval(inter);
                if(canvas) canvas.remove();
            }}, 2800);
        }})();
    " />
    """
    st.markdown(matrix_js, unsafe_allow_html=True)
    time.sleep(3.0)

def render_timer_and_flip(time_limit, question_key):
    if f"start_time_{question_key}" not in st.session_state:
        st.session_state[f"start_time_{question_key}"] = time.time()
    
    elapsed = time.time() - st.session_state[f"start_time_{question_key}"]
    remaining = max(0, int(time_limit - elapsed))
    
    html_code = f"""
    <div class="flip-card" id="myCard">
      <div class="flip-card-inner">
        <div class="flip-card-front">
          <h2 style="color:#00FFC8; font-family:monospace;">Tyd Oor: <span id="timer">{remaining}</span>s</h2>
        </div>
        <div class="flip-card-back" id="cardBack">
          <h2>TYD IS OM!</h2>
        </div>
      </div>
    </div>
    <script>
      let timeLeft = {remaining};
      let timerEl = document.getElementById('timer');
      let card = document.getElementById('myCard');
      let cardBack = document.getElementById('cardBack');
      
      if (timeLeft <= 0) {{
        card.classList.add('flip');
        cardBack.classList.add('flits-aktief');
      }} else {{
        let countdown = setInterval(function() {{
          timeLeft--;
          timerEl.innerText = timeLeft;
          if (timeLeft <= 0) {{
            clearInterval(countdown);
            card.classList.add('flip');
            cardBack.classList.add('flits-aktief');
          }}
        }}, 1000);
      }}
    </script>
    """
    st.components.v1.html(html_code, height=170)

def embed_retro_game():
    st.components.v1.html("""
    <div style="text-align:center; background:#111; padding:15px; border-radius:10px; border:2px solid #3e3e5e;">
        <canvas id="spaceInvaders" width="500" height="200" style="background:black; border:1px solid #00FFC8; display:block; margin:0 auto;"></canvas>
        <div style="margin-top:10px;">
            <button onclick="moveLeft()" style="padding:10px 20px; font-weight:bold; background:#1e1e2f; color:#00FFC8; border:1px solid #3e3e5e; border-radius:5px; cursor:pointer;">◀ Links</button>
            <button onclick="shoot()" style="padding:10px 25px; font-weight:bold; background:#00FFC8; color:black; border:none; border-radius:5px; margin:0 10px; cursor:pointer;">💥 SKIET</button>
            <button onclick="moveRight()" style="padding:10px 20px; font-weight:bold; background:#1e1e2f; color:#00FFC8; border:1px solid #3e3e5e; border-radius:5px; cursor:pointer;">Regs ▶</button>
        </div>
        <p style="color:#888; font-family:monospace; font-size:12px; margin-top:5px;">Gebruik die knoppies of jou sleutelbord (Pyltjies + Spasiebalk) om te speel!</p>
    </div>

    <script>
    const canvas = document.getElementById('spaceInvaders');
    const ctx = canvas.getContext('2d');

    let player = { x: 235, y: 175, width: 30, height: 15, speed: 12 };
    let bullets = [];
    let invaders = [];
    let gameOver = false;
    let score = 0;

    for(let r=0; r<2; r++) {
        for(let c=0; c<7; c++) {
            invaders.push({ x: c * 55 + 60, y: r * 30 + 30, width: 25, height: 15, alive: true });
        }
    }

    function moveLeft() { if(player.x > 0) player.x -= player.speed; }
    function moveRight() { if(player.x < canvas.width - player.width) player.x += player.speed; }
    function shoot() { bullets.push({ x: player.x + 13, y: player.y, speed: 6 }); }

    window.addEventListener('keydown', (e) => {
        if(e.key === 'ArrowLeft') moveLeft();
        if(e.key === 'ArrowRight') moveRight();
        if(e.key === ' ' || e.key === 'Spacebar') { shoot(); e.preventDefault(); }
    });

    function update() {
        if(gameOver) return;

        bullets.forEach((b, index) => {
            b.y -= b.speed;
            if(b.y < 0) bullets.splice(index, 1);
        });

        invaders.forEach(inv => {
            if(!inv.alive) return;
            bullets.forEach((b, bIdx) => {
                if(b.x > inv.x && b.x < inv.x + inv.width && b.y > inv.y && b.y < inv.y + inv.height) {
                    inv.alive = false;
                    bullets.splice(bIdx, 1);
                    score += 10;
                }
            });
        });

        if(invaders.every(i => !i.alive)) { gameOver = true; }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#00FFC8';
        ctx.fillRect(player.x, player.y, player.width, player.height);

        ctx.fillStyle = '#ff4b4b';
        bullets.forEach(b => ctx.fillRect(b.x, b.y, 4, 10));

        ctx.fillStyle = '#ffffff';
        invaders.forEach(inv => {
            if(inv.alive) ctx.fillRect(inv.x, inv.y, inv.width, inv.height);
        });

        ctx.fillStyle = '#00FFC8';
        ctx.font = '14px monospace';
        ctx.fillText('TELLING: ' + score, 10, 20);

        if(gameOver) {
            ctx.fillStyle = '#00FFC8';
            ctx.font = '24px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('SPELETTJIE VOLTOOI!', canvas.width/2, canvas.height/2);
        }

        requestAnimationFrame(draw);
    }

    setInterval(update, 1000/30);
    draw();
    </script>
    """, height=300)

# ==========================================
# 5. SUBJECT MODULES
# ==========================================
def module_wiskunde_algebra():
    st.markdown(f'### 🧮 Wiskunde - Algebra <span class="wetenskap-teks">(Vlak {st.session_state.level})</span>', unsafe_allow_html=True)
    
    if "algebra_q_index" not in st.session_state:
        st.session_state.algebra_q_index = 0

    vlak_1_vrae = [
        {"vraag": r"7 - 5 = ?", "korrek": "2"},
        {"vraag": r"1 - 7 = ?", "korrek": "-6"},
        {"vraag": r"6 \times 7 = ?", "korrek": "42"},
        {"vraag": r"\frac{8}{2} = ?", "korrek": "4"}
    ]
    
    vlak_2_vrae = [
        {"vraag": r"(5 \times 2) + (6 \times 3) = ?", "korrek": "28"}
    ]

    if st.session_state.level == 1:
        vrae_stel = vlak_1_vrae
    else:
        vrae_stel = vlak_2_vrae

    idx = st.session_state.algebra_q_index % len(vrae_stel)
    huidige_vraag = vrae_stel[idx]

    q_key = f"alg_{st.session_state.level}_{idx}"
    render_timer_and_flip(15, q_key)
    
    st.latex(huidige_vraag["vraag"])
    
    ans = st.text_input("Jou Antwoord:", key=f"alg_ans_{q_key}")
    
    if st.button("Dien In", key=f"alg_btn_{q_key}"):
        if ans.strip() == huidige_vraag["korrek"]:
            st.session_state.score += 10
            st.session_state.algebra_q_index += 1
            
            vlak_opgradeer = False
            volgende_vlak = st.session_state.level
            
            if st.session_state.level == 1 and st.session_state.algebra_q_index >= len(vlak_1_vrae):
                st.session_state.level = 2
                volgende_vlak = 2
                st.session_state.algebra_q_index = 0
                vlak_opgradeer = True
            elif st.session_state.level == 2 and st.session_state.algebra_q_index >= len(vlak_2_vrae):
                st.session_state.level += 1
                volgende_vlak = st.session_state.level
                st.session_state.algebra_q_index = 0
                vlak_opgradeer = True
                
            opdateer_leerder_data_in_db()
            
            if vlak_opgradeer:
                run_matrix_transition(volgende_vlak)
                st.rerun()
            else:
                st.balloons()
                st.success("Kompetisiepunt behaal!")
                time.sleep(2.0)
                st.rerun()
        else:
            st.error("Verkeerd. Probeer weer.")

def module_wiskunde_meetkunde():
    st.markdown(f'### 📐 Wiskunde - Meetkunde <span class="wetenskap-teks">(Vlak {st.session_state.level})</span>', unsafe_allow_html=True)
    
    graph = graphviz.Digraph()
    if st.session_state.level == 1:
        graph.node('A', shape='square', label='Vierkant\nSye = 5cm')
        correct = "25"
    elif st.session_state.level == 2:
        graph.node('A', shape='box', label='Reghoek\nL=6cm, B=4cm')
        correct = "24"
    else:
        graph.node('A', shape='triangle', label='Driehoek\nB=4cm, H=5cm')
        correct = "10"
        
    q_key = f"meet_{st.session_state.level}"
    render_timer_and_flip(20, q_key)
    
    st.graphviz_chart(graph)
    st.subheader("Wat is die area (oppervlakte)?")
    
    ans = st.text_input("Antwoord in cm²:", key=f"meet_ans_{q_key}")
    if st.button("Dien In", key=f"meet_btn_{q_key}"):
        if ans == correct:
            st.session_state.score += 15
            
            if st.session_state.score % 45 == 0:
                st.session_state.level += 1
                volgende_vlak = st.session_state.level
                opdateer_leerder_data_in_db()
                run_matrix_transition(volgende_vlak)
                st.rerun()
            else:
                opdateer_leerder_data_in_db()
                st.snow()
                st.success("Uitstekend!")
                time.sleep(2.0)
                st.rerun()
        else:
            st.error("Oeps!")

def module_lees_begrip(taal):
    st.markdown(f'### 📖 {taal} - Lees <span class="wetenskap-teks">(Begripstoets)</span>', unsafe_allow_html=True)
    text = "Daar was eenmaal 'n vinnige jakkals wat oor die lui hond gespring het." if taal == "Afrikaans" else "The quick brown fox jumps over the lazy dog."
    
    st.info(text)
    
    game_key = f"game_done_{taal.lower()}"
    if game_key not in st.session_state:
        st.session_state[game_key] = False

    if not st.session_state[game_key]:
        st.markdown("---")
        st.subheader("👾 Speel eers hierdie vinnige retro-speletjie om jou vrae te ontsluit:")
        embed_retro_game()
        
        if st.button("🎮 Ek het die speletjie klaar gespeel! Wys my vrae"):
            st.session_state[game_key] = True
            st.rerun()
    else:
        st.success("✅ Speletjie voltooi! Jou timer het nou begin.")
        
        q_key = f"lees_{taal.lower()}"
        render_timer_and_flip(20, q_key)
        
        st.markdown("---")
        q = "Oor wie het die jakkals gespring?" if taal == "Afrikaans" else "Who did the fox jump over?"
        ans = st.text_input(q, key=f"lees_ans_{q_key}")
        
        if st.button("Dien In", key=f"lees_btn_{q_key}"):
            if "hond" in ans.lower() or "dog" in ans.lower():
                st.balloons()
                st.success("Mooi so!")
                st.session_state.score += 20
                
                st.session_state[game_key] = False
                opdateer_leerder_data_in_db()
                time.sleep(2.0)
                st.rerun()
            else:
                st.error("Oeps, probeer weer!")

# ==========================================
# 6. DASHBOARDS (FRONT PAGE & ADMIN)
# ==========================================
def front_page():
    st.markdown(f'<div class="hoof-kaart">Welkom terug, {st.session_state.user["avatar"]} <span class="wetenskap-teks">{st.session_state.user["name"]}</span></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Huidige Telling", value=st.session_state.score)
    with col2:
        st.metric(label="Jou Hoogste Vlak", value=st.session_state.max_level)
    
    st.markdown("### 🏆 Top 10 Kampioene")
    db = load_db()
    users_list = list(db["users"].values())
    if users_list:
        df = pd.DataFrame(users_list)
        if "score" in df.columns:
            if "max_level" not in df.columns:
                df["max_level"] = df["level"]
            else:
                df["max_level"] = df["max_level"].fillna(df["level"])
                
            df = df.sort_values(by="score", ascending=False).head(10)
            st.dataframe(df[['avatar', 'name', 'max_level', 'score']], use_container_width=True, hide_index=True)
    
    st.markdown("### 📈 Jou Spoed Oor Tyd")
    chart_data = pd.DataFrame({'Tyd (Sekondes)': [12, 10, 8, 9, 6]}, index=['Vraag 1', 'Vraag 2', 'Vraag 3', 'Vraag 4', 'Vraag 5'])
    st.line_chart(chart_data)

def admin_dashboard():
    st.title("👨‍🏫 Onderwyser Dashboard")
    db = load_db()
    
    st.subheader("Alle Studente Statestiek")
    df = pd.DataFrame(list(db["users"].values()))
    st.dataframe(df)
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Laai Resultate Af (CSV vir Excel)",
            data=csv,
            file_name=f"stats_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

# ==========================================
# 7. MAIN ROUTING & SIDEBAR
# ==========================================
def stop_en_gaan_na_voorblad():
    st.session_state.playing = False
    st.session_state.category_selection = "Voorblad (Stats & Leaderboard)"
    st.session_state.previous_category = "Voorblad (Stats & Leaderboard)"
    st.session_state.selected_category = "Voorblad (Stats & Leaderboard)"

def main():
    if st.session_state.user is None:
        login_flow()
        return

    if st.session_state.user.get("role") == "admin":
        if st.sidebar.button("Log Uit"):
            st.session_state.clear()
            st.rerun()
        admin_dashboard()
        return

    if "selected_category" not in st.session_state:
        st.session_state.selected_category = "Voorblad (Stats & Leaderboard)"

    with st.sidebar:
        st.markdown(f"## {st.session_state.user['avatar']} {st.session_state.user['name']}")
        st.markdown(f"**Hoogste Vlak:** {st.session_state.max_level} | **Punte:** {st.session_state.score}")
        st.markdown("---")
        
        category = st.selectbox("Kies Kategorie", [
            "Voorblad (Stats & Leaderboard)",
            "Wiskunde - Algebra", 
            "Wiskunde - Meetkunde", 
            "Afrikaans - Taal", 
            "Afrikaans - Lees", 
            "Engels - Taal", 
            "Engels - Lees"
        ], key="category_selection")
        
        if "previous_category" not in st.session_state:
            st.session_state.previous_category = category

        if category != st.session_state.previous_category:
            st.session_state.level = 1
            if "algebra_q_index" in st.session_state:
                st.session_state.algebra_q_index = 0
            st.session_state.previous_category = category
            opdateer_leerder_data_in_db()
            
        st.session_state.selected_category = category
        
        st.markdown("---")
        st.button("⏹ Stop en Gaan na Voorblad", on_click=stop_en_gaan_na_voorblad)
            
        if st.button("Log Uit"):
            st.session_state.clear()
            st.rerun()

    if st.session_state.selected_category == "Voorblad (Stats & Leaderboard)":
        front_page()
    else:
        st.session_state.playing = True
        if st.session_state.selected_category == "Wiskunde - Algebra": module_wiskunde_algebra()
        elif st.session_state.selected_category == "Wiskunde - Meetkunde": module_wiskunde_meetkunde()
        elif st.session_state.selected_category == "Afrikaans - Taal": st.write("Afrikaans Taal Module - (Laai vrae manueel in DB)")
        elif st.session_state.selected_category == "Afrikaans - Lees": module_lees_begrip("Afrikaans")
        elif st.session_state.selected_category == "Engels - Taal": st.write("Engels Taal Module - (Laai vrae manueel in DB)")
        elif st.session_state.selected_category == "Engels - Lees": module_lees_begrip("Engels")

if __name__ == "__main__":
    main()