import sys
import os

# --- 1. LIGAÇÃO AO UTILS (CRÍTICO) ---
# Isto garante que encontramos o ficheiro 'utils.py' na pasta de trás
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

import streamlit as st
import utils # Importa o nosso gestor de chaves

# --- 2. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Compliance Ambiental", page_icon="🌿", layout="wide")

# --- 3. CARREGAR BARRA LATERAL ---
# Isto vai mostrar a chave que já inseriu, sem pedir de novo
utils.sidebar_comum()

# --- 4. VERIFICAÇÃO DE SEGURANÇA ---
# Lemos a chave diretamente da memória global
api_key = st.session_state.get("api_key", "")

if not api_key:
    st.error("🛑 **ACESSO BLOQUEADO**: A API Key não foi detetada.")
    st.info("⬅️ Por favor, insira a chave na **barra lateral esquerda** e pressione Enter.")
    st.stop() # Pára o código aqui até haver chave

# ==========================================
# DAQUI PARA BAIXO: O SEU CÓDIGO DA APP
# ==========================================
import google.generativeai as genai
# ... (Resto dos imports e lógica da app ambiente.py) ...

st.title("🌿 Módulo de Ambiente Ativo")
st.write("A chave está a funcionar e pronta a usar!")

# (Cole aqui o resto do seu código original do módulo 3...)
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tempfile

st.set_page_config(page_title="Gestão de Prazos", page_icon="📅", layout="wide")

try:
    utils.sidebar_comum()
except:
    pass

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

# ==========================================
# 2. MOTOR DE FERIADOS (CÓDIGO COMPLETO)
# ==========================================

def get_easter_date(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def get_holidays_for_year(year):
    holidays = set()
    fixed_dates = [(1, 1), (4, 25), (5, 1), (6, 10), (8, 15), (10, 5), (11, 1), (12, 1), (12, 8), (12, 25)]
    for m, d in fixed_dates:
        holidays.add(date(year, m, d))
    easter = get_easter_date(year)
    holidays.add(easter - timedelta(days=2))
    holidays.add(easter + timedelta(days=60))
    return holidays

def get_holidays_range(start_year, end_year):
    all_holidays = set()
    for y in range(start_year, end_year + 1):
        all_holidays.update(get_holidays_for_year(y))
    return all_holidays

def is_business_day(check_date, holidays_set):
    if check_date.weekday() >= 5: return False
    if check_date in holidays_set: return False
    return True

def add_business_days(start_date, num_days, holidays_set):
    current_date = start_date
    added_days = 0
    while added_days < num_days:
        current_date += timedelta(days=1)
        if is_business_day(current_date, holidays_set):
            added_days += 1
    return current_date

def is_suspended(current_date, suspensions):
    for s in suspensions:
        if s['start'] <= current_date <= s['end']:
            return True
    return False

def calculate_deadline_rigorous(start_date, target_business_days, suspensions, holidays_set, return_log=False):
    current_date = start_date
    days_counted = 0
    log = []
    if return_log:
        log.append({"Data": current_date, "Dia Contado": 0, "Status": "Início"})
    while days_counted < target_business_days:
        current_date += timedelta(days=1)
        status = "Util"
        if is_suspended(current_date, suspensions):
            status = "Suspenso"
        elif current_date.weekday() >= 5:
            status = "Fim de Semana"
        elif current_date in holidays_set:
            status = "Feriado"
        if status == "Util":
            days_counted += 1
        if return_log:
            log.append({"Data": current_date, "Dia Contado": days_counted if status == "Util" else "-", "Status": status})
    final_date = current_date
    while final_date.weekday() >= 5 or final_date in holidays_set:
         final_date += timedelta(days=1)
    if return_log:
        return final_date, log
    return final_date

def calculate_workflow(start_date, suspensions, milestones_config, pea_date=None):
    holidays_set = get_holidays_range(start_date.year, start_date.year + 2)
    results = []
    log_final = []
    steps = [
        ("Data Reunião", milestones_config["reuniao"]),
        ("Limite Conformidade", milestones_config["conformidade"]),
        ("Envio PTF à AAIA", milestones_config["ptf"]),
        ("Audiência de Interessados", milestones_config["audiencia"]),
        ("Emissão da DIA (Decisão Final)", milestones_config["dia"])
    ]
    conf_date_real = None 
    for nome, dias in steps:
        final_date = None
        if nome == "Limite Conformidade" and pea_date and suspensions:
            days_spent = 0
            check_date = start_date + timedelta(days=1)
            while check_date < pea_date:
                if is_business_day(check_date, holidays_set):
                    days_spent += 1
                check_date += timedelta(days=1)
            remaining_days = dias - days_spent
            if remaining_days < 0: remaining_days = 0
            last_susp_end = max([s['end'] for s in suspensions])
            final_date = calculate_deadline_rigorous(last_susp_end, remaining_days, [], holidays_set)
            conf_date_real = final_date
        else:
            if dias == milestones_config["dia"]: 
                final_date, log_data = calculate_deadline_rigorous(start_date, dias, suspensions, holidays_set, return_log=True)
                log_final = log_data
            else:
                final_date = calculate_deadline_rigorous(start_date, dias, suspensions, holidays_set)
            if nome == "Limite Conformidade":
                conf_date_real = final_date
        results.append({
            "Etapa": nome, 
            "Prazo Legal": f"{dias} dias úteis", 
            "Data Prevista": final_date
        })

    complementary = []
    gantt_data = {}
    if conf_date_real:
        cp_duration = milestones_config.get("cp_duration", 30)
        visit_days = milestones_config.get("visita", 15)
        sectoral_days = milestones_config.get("setoriais", 75)
        conf_date_theo = calculate_deadline_rigorous(start_date, milestones_config["conformidade"], [], holidays_set)
        cp_start = add_business_days(conf_date_real, 5, holidays_set)
        cp_end = add_business_days(cp_start, cp_duration, holidays_set)
        external_ops = add_business_days(cp_start, 23, holidays_set)
        cp_report = add_business_days(cp_end, 7, holidays_set)
        visit_date = add_business_days(cp_start, visit_days, holidays_set)
        sectoral_date = calculate_deadline_rigorous(start_date, sectoral_days, suspensions, holidays_set)
        gantt_data = {"cp_start": cp_start, "cp_end": cp_end, "visit": visit_date, "sectoral": sectoral_date}
        complementary = [
            {"Etapa": "1. Conformidade (Ref. Teórica)", "Ref": "Sem suspensões", "Data": conf_date_theo},
            {"Etapa": "1. Conformidade (Real)", "Ref": "Com suspensões", "Data": conf_date_real},
            {"Etapa": "2. Início Consulta Pública", "Ref": "Conf + 5 dias", "Data": cp_start},
            {"Etapa": "3. Fim Consulta Pública", "Ref": f"Início CP + {cp_duration} dias", "Data": cp_end},
            {"Etapa": "4. Data Pareceres Externos", "Ref": "Início CP + 23 dias", "Data": external_ops},
            {"Etapa": "5. Envio Relatório CP", "Ref": "Fim CP + 7 dias", "Data": cp_report},
            {"Etapa": "6. Visita Técnica", "Ref": f"Início CP + {visit_days} dias", "Data": visit_date},
            {"Etapa": "7. Pareceres Setoriais", "Ref": f"Dia {sectoral_days} Global", "Data": sectoral_date},
        ]

    total_susp = sum([(s['end'] - s['start']).days + 1 for s in suspensions])
    return results, complementary, total_susp, log_final, gantt_data

def create_pdf(project_name, typology, sector, regime, start_date, milestones, complementary, suspensions, total_susp, gantt_data):
    if FPDF is None: return None
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 10)
            self.set_text_color(30, 58, 138)
            self.cell(0, 10, 'AUTORIDADE DE AIA', 0, 1, 'C')
            self.line(10, 20, 200, 20)
            self.ln(10)
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(15, 23, 42)
    pdf.multi_cell(0, 10, f"Relatorio de Prazos: {project_name}", align='L')
    pdf.ln(5)
    
    # 1. Enquadramento
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "1. Enquadramento e Legislacao", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)
    pdf.cell(40, 6, "Tipologia:", 0, 0)
    pdf.multi_cell(0, 6, typology)
    pdf.cell(40, 6, "Setor:", 0, 0)
    pdf.cell(0, 6, sector, 0, 1)
    pdf.ln(2)
    
    # 2. Resumo
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "2. Resumo", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.set_font("Arial", "", 10)
    pdf.cell(50, 6, "Regime:", 0, 0)
    pdf.cell(0, 6, f"{regime}", 0, 1)
    pdf.cell(50, 6, "Data de Instrucao:", 0, 0)
    pdf.cell(0, 6, start_date.strftime('%d/%m/%Y'), 0, 1)
    pdf.cell(50, 6, "Total Suspensao:", 0, 0)
    pdf.cell(0, 6, f"{total_susp} dias", 0, 1)
    pdf.ln(5)

    # 3. Cronograma Oficial
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "3. Cronograma Oficial (Fases Principais)", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(226, 232, 240)
    pdf.cell(90, 8, "Etapa", 1, 0, 'L', 1)
    pdf.cell(40, 8, "Prazo Legal", 1, 0, 'C', 1)
    pdf.cell(40, 8, "Data Prevista", 1, 1, 'C', 1)
    pdf.set_font("Arial", "", 9)
    pdf.ln()
    for m in milestones:
        pdf.cell(90, 8, m["Etapa"].encode('latin-1','replace').decode('latin-1'), 1)
        pdf.cell(40, 8, str(m["Prazo Legal"]), 1, 0, 'C')
        pdf.cell(40, 8, m["Data Prevista"].strftime('%d/%m/%Y'), 1, 0, 'C')
        pdf.ln()

    # 4. Cronograma Visual
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "5. Cronograma Visual (Gantt)", 0, 1)
    try:
        tasks = []
        start_dates = []
        end_dates = []
        colors = []
        last = start_date
        for m in milestones:
            end = m["Data Prevista"]
            start = last if last < end else end
            tasks.append(m["Etapa"])
            start_dates.append(start)
            end_dates.append(end)
            colors.append('skyblue')
            last = end
        for s in suspensions:
            tasks.append("Suspensao")
            start_dates.append(s['start'])
            end_dates.append(s['end'])
            colors.append('salmon')
        if gantt_data:
            tasks.append("Consulta Publica")
            start_dates.append(gantt_data['cp_start'])
            end_dates.append(gantt_data['cp_end'])
            colors.append('lightgreen')

        fig, ax = plt.subplots(figsize=(10, 6))
        for i, task in enumerate(tasks):
            start_num = mdates.date2num(start_dates[i])
            end_num = mdates.date2num(end_dates[i])
            duration = end_num - start_num
            if duration < 1: duration = 1
            ax.barh(task, duration, left=start_num, color=colors[i], align='center', edgecolor='grey')
            
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        plt.xticks(rotation=45)
        plt.grid(axis='x', linestyle='--', alpha=0.5)
        plt.tight_layout()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            plt.savefig(tmpfile.name, dpi=100)
            tmp_filename = tmpfile.name
        pdf.image(tmp_filename, x=10, y=30, w=190)
        plt.close(fig)
        os.unlink(tmp_filename)
    except Exception as e:
        pdf.ln(5)
        pdf.cell(0, 10, f"Erro no grafico: {str(e)}", 0, 1)

    return pdf.output(dest='S').encode('latin-1')

# --- UI ---
st.title("🌿 Gestão de Prazos AIA")
with st.sidebar:
    st.markdown("---")
    proj_name = st.text_input("Nome do Projeto", "Novo Projeto AIA")
    start_date = st.date_input("Data de Instrução (Dia 0)", date.today())
    
    TIPOLOGIAS_INFO = {"Anexo I": "Anexo I", "Anexo II": "Anexo II", "Alteração": "Alt."}
    selected_typology = st.selectbox("Tipologia", list(TIPOLOGIAS_INFO.keys()))
    SPECIFIC_LAWS = {"Indústria": {}, "Energia": {}, "Outros": {}}
    selected_sector = st.selectbox("Setor", list(SPECIFIC_LAWS.keys()))
    
    regime_option = st.radio("Prazo Global:", (150, 90))
    
    with st.expander("Definições Avançadas"):
        if regime_option == 150:
            d_reuniao = st.number_input("Reunião", 9)
            d_conf = st.number_input("Conformidade", 30)
            d_ptf = st.number_input("Envio PTF", 85)
            d_aud = st.number_input("Audiência", 100)
            d_dia = st.number_input("Decisão", 150, disabled=True)
            d_setoriais = 75
        else:
            d_reuniao = st.number_input("Reunião", 9)
            d_conf = st.number_input("Conformidade", 20)
            d_ptf = st.number_input("Envio PTF", 65)
            d_aud = st.number_input("Audiência", 70)
            d_dia = st.number_input("Decisão", 90, disabled=True)
            d_setoriais = 60
        d_cp_duration = st.number_input("CP Duração", 30)
        d_visita = st.number_input("Visita", 15)
        pea_date = st.date_input("Data PEA", value=None)
        
        milestones_config = {
            "reuniao": d_reuniao, "conformidade": d_conf, "ptf": d_ptf,
            "audiencia": d_aud, "dia": d_dia,
            "visita": d_visita, "setoriais": d_setoriais, "cp_duration": d_cp_duration
        }

    st.markdown("---")
    if 'suspensions_universal' not in st.session_state: st.session_state.suspensions_universal = []
    
    with st.form("add_susp_uni", clear_on_submit=True):
        c1, c2 = st.columns(2)
        new_start = c1.date_input("Início")
        new_end = c2.date_input("Fim")
        if st.form_submit_button("Adicionar"):
            st.session_state.suspensions_universal.append({'start': new_start, 'end': new_end})
            st.rerun()
    
    for i, s in enumerate(st.session_state.suspensions_universal):
        st.text(f"{s['start']} a {s['end']}")
        if st.button("X", key=f"rm_{i}"):
            del st.session_state.suspensions_universal[i]
            st.rerun()

milestones, complementary, total_susp, log_dia, gantt_data = calculate_workflow(
    start_date, st.session_state.suspensions_universal, milestones_config, pea_date=pea_date
)

final_dia_date = milestones[-1]["Data Prevista"]
st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Regime", f"{regime_option} Dias")
c2.metric("Início", start_date.strftime("%d/%m/%Y"))
c3.metric("Suspensões", f"{total_susp} dias")
c4.metric("Previsão DIA", final_dia_date.strftime("%d/%m/%Y"))

tab1, tab2, tab3 = st.tabs(["📋 Prazos", "📅 Gantt", "📄 PDF"])

with tab1:
    df_main = pd.DataFrame(milestones)
    df_main["Data Prevista"] = pd.to_datetime(df_main["Data Prevista"]).dt.strftime("%d-%m-%Y")
    st.dataframe(df_main, use_container_width=True)
    if complementary:
        st.write("Prazos Complementares")
        df_comp = pd.DataFrame(complementary)
        df_comp["Data"] = pd.to_datetime(df_comp["Data"]).dt.strftime("%d-%m-%Y")
        st.dataframe(df_comp, use_container_width=True)

with tab2:
    data_gantt = []
    last = start_date
    for m in milestones:
        end = m["Data Prevista"]
        start = last if last < end else end
        data_gantt.append(dict(Task=m["Etapa"], Start=start, Finish=end, Resource="Fase Principal"))
        last = end
    for s in st.session_state.suspensions_universal:
        data_gantt.append(dict(Task="Suspensão", Start=s['start'], Finish=s['end'], Resource="Suspensão"))
        
    fig = px.timeline(pd.DataFrame(data_gantt), x_start="Start", x_end="Finish", y="Task", color="Resource")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    if st.button("Gerar Relatório PDF"):
        pdf_bytes = create_pdf(
            proj_name, selected_typology, selected_sector, f"Regime {regime_option} Dias", 
            start_date, milestones, complementary, st.session_state.suspensions_universal, 
            total_susp, gantt_data
        )
        if pdf_bytes:

            st.download_button("Descarregar PDF", pdf_bytes, "relatorio_aia.pdf", "application/pdf")
