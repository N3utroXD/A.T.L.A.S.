import flet as ft
import asyncio
import spotipy
import sqlite3
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth
from flet import Text, Row, Container, FilledButton, TextButton, TextField, Column, Divider


#Telemetria
def init_db():
    conn = sqlite3.connect("atlas.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS historico (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data TEXT,
                        materia TEXT,
                        minutos INTEGER)''')
    conn.commit()
    conn.close()


def salvar_sessao(materia, minutos):
    conn = sqlite3.connect("atlas.db")
    cursor = conn.cursor()
    data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO historico (data, materia, minutos) VALUES (?, ?, ?)",
                   (data_hoje, materia, minutos))
    conn.commit()
    conn.close()


def buscar_dados_telemetria():
    conn = sqlite3.connect("atlas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT materia, SUM(minutos) FROM historico GROUP BY materia ORDER BY SUM(minutos) DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados


#Configurações do Spotify
MEU_CLIENT_ID = "2fc2341bd1cb408f839cca220205feb7"
MEU_CLIENT_SECRET = "9bcd4ed5b28147fbbcb9377f7e752ed1"
PLAYLIST_URI = "https://open.spotify.com/playlist/0MPwIUL2Wm57tADhTFJGR4?si=0riAuQJ-QS2GBBo1k3y0Qg"

autenticacao = SpotifyOAuth(
    client_id=MEU_CLIENT_ID,
    client_secret=MEU_CLIENT_SECRET,
    redirect_uri="http://127.0.0.1:8888",
    scope="user-modify-playback-state"
)
sp = spotipy.Spotify(auth_manager=autenticacao)


def main(page: ft.Page):
    init_db()

    page.window.width = 360
    page.window.height = 640
    page.title = "A.T.L.A.S."
    page.window.always_on_top = True

    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.theme_mode = "dark"
    page.scroll = "auto"

    tempo_padrao_foco = 50 * 60
    tempo_descanso = 10 * 60

    tempo_foco_atual = tempo_padrao_foco
    tempo_restante = tempo_foco_atual
    a_correr = False
    em_foco = True
    tarefas = []

    def adicionar_tarefa(e):
        nome_tarefa = input_tarefa.value.strip()
        tempo_texto = input_tempo.value.strip()

        if nome_tarefa != "":
            if tempo_texto.isdigit():
                minutos = int(tempo_texto)
            else:
                minutos = 50

            nova_tarefa = {"nome": nome_tarefa, "tempo": minutos * 60}
            tarefas.append(nova_tarefa)
            lista_visual.controls.append(Text(f"• {nome_tarefa} ({minutos} min)", size=16))

            if len(tarefas) == 1 and not a_correr and em_foco:
                nonlocal tempo_foco_atual, tempo_restante
                tempo_foco_atual = tarefas[0]["tempo"]
                tempo_restante = tempo_foco_atual
                titulo_tarefa.value = f"Foco: {tarefas[0]['nome']}"
                relogio.value = formatar_tempo(tempo_restante)

            input_tarefa.value = ""
            input_tempo.value = ""
            input_tarefa.focus()
            page.update()

    def formatar_tempo(segundos):
        minutos = segundos // 60
        segs = segundos % 60
        return f"{minutos:02d}:{segs:02d}"

    titulo_tarefa = Text("Foco: A aguardar missões...", size=20, weight="bold")
    relogio = Text(formatar_tempo(tempo_restante), size=70, weight="bold", color="blue")

    titulo_fila = Text("Fila de Estudos", size=16, weight="bold", color="grey")
    input_tarefa = TextField(hint_text="Matéria", expand=True, on_submit=adicionar_tarefa)
    input_tempo = TextField(hint_text="Min.", width=70, keyboard_type="number", on_submit=adicionar_tarefa)
    botao_add = FilledButton("+", on_click=adicionar_tarefa, width=60)

    linha_input = Row([input_tarefa, input_tempo, botao_add])
    lista_visual = Column()

    painel_stats = Column(visible=False, horizontal_alignment="center")

    def alternar_dashboard(e):

        painel_stats.controls.clear()

        if not painel_stats.visible:
            painel_stats.controls.append(Text("TELEMETRIA", weight="bold", color="red"))

            dados = buscar_dados_telemetria()
            if not dados:
                painel_stats.controls.append(Text("Nenhuma missão registada.", color="grey"))
            else:
                for materia, minutos in dados:
                    horas = minutos // 60
                    mins = minutos % 60
                    if horas > 0:
                        tempo_formatado = f"{horas}h {mins}m" if mins > 0 else f"{horas}h"
                    else:
                        tempo_formatado = f"{mins}m"

                    painel_stats.controls.append(Text(f"• {materia}: {tempo_formatado}", size=14, color="white"))

            painel_stats.controls.append(Divider(height=20, color="transparent"))

        painel_stats.visible = not painel_stats.visible
        page.update()

    botao_telemetria = TextButton("(#)", on_click=alternar_dashboard)
    cabecalho = Row([botao_telemetria], alignment="end")

    async def atualizar_relogio():
        nonlocal tempo_restante, a_correr, em_foco, tempo_foco_atual
        while a_correr:
            if tempo_restante > 0:
                await asyncio.sleep(1)
                tempo_restante -= 1
                relogio.value = formatar_tempo(tempo_restante)
                page.update()
            else:
                em_foco = not em_foco

                if em_foco:
                    if tarefas:
                        tarefas.pop(0)
                        if lista_visual.controls:
                            lista_visual.controls.pop(0)

                    if tarefas:
                        proxima = tarefas[0]["nome"]
                        tempo_foco_atual = tarefas[0]["tempo"]
                    else:
                        proxima = "Estudo Livre"
                        tempo_foco_atual = tempo_padrao_foco

                    tempo_restante = tempo_foco_atual
                    titulo_tarefa.value = f"Foco: {proxima}"
                    titulo_tarefa.color = "white"
                    relogio.color = "blue"

                    try:
                        sp.shuffle(True)
                        sp.start_playback(context_uri=PLAYLIST_URI)
                    except Exception:
                        pass
                else:
                    materia_concluida = tarefas[0]["nome"] if tarefas else "Estudo Livre"
                    minutos_foco = tempo_foco_atual // 60
                    salvar_sessao(materia_concluida, minutos_foco)

                    tempo_restante = tempo_descanso
                    titulo_tarefa.value = "Descanso"
                    titulo_tarefa.color = "green"
                    relogio.color = "green"

                    try:
                        sp.pause_playback()
                    except Exception:
                        pass

                relogio.value = formatar_tempo(tempo_restante)
                page.update()

    async def alternar_timer(e):
        nonlocal a_correr
        a_correr = not a_correr
        if a_correr:
            botao_play.text = "Pausar"
            page.update()
            if em_foco:
                try:
                    sp.shuffle(True)
                    sp.start_playback(context_uri=PLAYLIST_URI)
                except Exception:
                    pass
            asyncio.create_task(atualizar_relogio())
        else:
            botao_play.text = "Retomar"
            page.update()
            try:
                sp.pause_playback()
            except Exception:
                pass

    def reiniciar_timer(e):
        nonlocal a_correr, tempo_restante, em_foco, tempo_foco_atual
        a_correr = False
        em_foco = True

        if tarefas:
            tempo_foco_atual = tarefas[0]["tempo"]
            titulo_tarefa.value = f"Foco: {tarefas[0]['nome']}"
        else:
            tempo_foco_atual = tempo_padrao_foco
            titulo_tarefa.value = "Foco: A aguardar missões..."

        tempo_restante = tempo_foco_atual
        relogio.value = formatar_tempo(tempo_restante)
        relogio.color = "blue"
        botao_play.text = "Iniciar"
        titulo_tarefa.color = "white"
        page.update()
        try:
            sp.pause_playback()
        except Exception:
            pass

    def pular_musica(e):
        try:
            sp.next_track()
        except Exception:
            pass

    botao_play = FilledButton("Iniciar", on_click=alternar_timer, width=120)
    botao_pular = FilledButton(">", on_click=pular_musica, width=60)
    botao_reset = TextButton("Reiniciar", on_click=reiniciar_timer, width=120)

    page.add(
        cabecalho,
        painel_stats,
        titulo_tarefa,
        Container(height=10),
        relogio,
        Container(height=10),
        Row([botao_play, botao_pular, botao_reset], alignment="center"),
        Divider(height=40, color="transparent"),
        titulo_fila,
        linha_input,
        lista_visual
    )


ft.run(main)
