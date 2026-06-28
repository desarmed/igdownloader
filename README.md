# IG Baixador

Baixador pessoal de conteúdo do Instagram (reels, posts, stories, destaques).
Roda no seu PC, do seu IP e da sua sessão logada — por isso funciona quando os
sites públicos de download estão fora do ar.

## Usar
1. Abra o **IG-Baixador** (Windows: `IG-Baixador.exe`; Mac: arraste o `.dmg` e,
   na 1ª vez, botão direito → Abrir).
2. Esteja logado no Instagram **no Chrome**.
3. Cole o link, escolha a pasta, clique **Baixar**.

## Se der erro de cookies
- "Feche o Chrome e tente de novo" → o Chrome estava travando os cookies.
- Alternativa estável (`cookies.txt`): instale a extensão "Get cookies.txt LOCALLY",
  exporte os cookies do instagram.com pra um arquivo e aponte o app pra ele
  (config: `cookie_mode="cookies_txt"`, `cookies_txt_path=<arquivo>`).

## Desenvolver
```
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
# baixar binários (ver docs/superpowers/plans) e rodar:
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m ig_baixador
```
