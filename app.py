
import os
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import yaml

# -------- Pfade & Basis --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "expenses.csv")
CAT_PATH = os.path.join(BASE_DIR, "config", "categories.yaml")
FX_PATH = os.path.join(BASE_DIR, "config", "fx.yaml")

st.set_page_config(page_title="Ausgaben-Tracker", page_icon="💸", layout="centered")

# -------- Hilfsfunktionen --------
def ensure_files():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        pd.DataFrame(columns=["datum","betrag","währung","kategorie","händler","zahlung","notiz"]).to_csv(DATA_PATH, index=False)
    if not os.path.exists(CAT_PATH):
        with open(CAT_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump({"kategorien": ["Lebensmittel","Restaurant","Bar","Steuer","Hausunterhalt","Auto","Hotel","Transport","Gesundheit","Reisen","Sonstiges"]}, f, allow_unicode=True)
    if not os.path.exists(FX_PATH):
        with open(FX_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump({"basis": "EUR", "kurse": {"EUR": 1.0, "TRY": 0.03}}, f, allow_unicode=True)

def load_categories():
    with open(CAT_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("kategorien", [])

def load_fx():
    with open(FX_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    basis = data.get("basis", "EUR")
    kurse = data.get("kurse", {"EUR":1.0})
    return basis, kurse

def load_df():
    df = pd.read_csv(DATA_PATH, dtype=str)
    if df.empty:
        return df
    df["datum"] = pd.to_datetime(df["datum"], errors="coerce")
    df["betrag"] = pd.to_numeric(df["betrag"], errors="coerce")
    return df

def save_df(df: pd.DataFrame):
    out = df.copy()
    out["datum"] = out["datum"].dt.strftime("%Y-%m-%d")
    out.to_csv(DATA_PATH, index=False)

def convert_to_base(df: pd.DataFrame, basis: str, kurse: dict):
    df = df.copy()
    df["währung"] = df["währung"].fillna(basis)
    df["kurs"] = df["währung"].map(lambda w: kurse.get(w, 1.0))
    df["betrag_basis"] = df["betrag"] * df["kurs"]
    return df

# -------- UI --------
ensure_files()
basis, kurse = load_fx()
kategorien = load_categories()

st.markdown("## 💸 Ausgaben-Tracker (Web)")
st.caption("Datum wird automatisch auf **heute** gesetzt, ist aber änderbar.")

with st.form("eingabe"):
    col1, col2 = st.columns(2)
    datum = col1.date_input("Datum", value=date.today())
    betrag = col2.number_input("Betrag", min_value=0.0, step=0.5, format="%.2f")
    col3, col4 = st.columns(2)
    waehrung = col3.selectbox("Währung", options=list(kurse.keys()))
    zahlung = col4.selectbox("Zahlung", options=["Karte","Bar","Überweisung","Dauerauftrag"])
    kategorie = st.selectbox("Kategorie", options=kategorien)
    haendler = st.text_input("Händler (optional)")
    notiz = st.text_input("Notiz (optional)")
    submitted = st.form_submit_button("Speichern")

if submitted:
    df = load_df()
    new_row = {
        "datum": pd.to_datetime(datum),
        "betrag": float(betrag),
        "währung": waehrung,
        "kategorie": kategorie,
        "händler": haendler if haendler.strip() else None,
        "zahlung": zahlung,
        "notiz": notiz if notiz.strip() else None,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_df(df)
    st.success("Gespeichert.")

st.markdown("---")
st.markdown("### Analyse")

df = load_df()
if df.empty:
    st.info("Noch keine Daten. Trage oben deine erste Ausgabe ein.")
else:
    df = df.dropna(subset=["datum","betrag"])
    df = convert_to_base(df, basis, kurse)
    df["monat"] = df["datum"].dt.to_period("M").astype(str)

    total = df["betrag_basis"].sum()
    st.metric(f"Gesamt ({basis})", f"{total:,.2f} {basis}")

    # Tabellen
    st.markdown("**Ausgaben (Basiswährung)**")
    st.dataframe(df[["datum","betrag","währung","betrag_basis","kategorie","händler","zahlung","notiz"]].sort_values("datum"))

    by_cat = df.groupby("kategorie", dropna=False)["betrag_basis"].sum().sort_values(ascending=False).reset_index()
    by_month = df.groupby("monat")["betrag_basis"].sum().reset_index()

    st.markdown("**Summe nach Kategorie**")
    st.dataframe(by_cat)

    st.markdown("**Summe pro Monat**")
    st.dataframe(by_month)

    # Diagramme
    st.markdown("**Diagramme**")
    fig1 = plt.figure()
    plt.bar(by_cat["kategorie"].astype(str), by_cat["betrag_basis"])
    plt.title(f"Ausgaben nach Kategorie ({basis})")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig1)

    fig2 = plt.figure()
    plt.plot(by_month["monat"], by_month["betrag_basis"], marker="o")
    plt.title(f"Ausgaben pro Monat ({basis})")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig2)

st.markdown("---")
with st.expander("⚙️ Einstellungen"):
    st.write("**Basiswährung & Wechselkurse** in `config/fx.yaml` anpassen. Beispiel:")
    st.code("basis: \"EUR\"\nkurse:\n  EUR: 1.0\n  TRY: 0.028", language="yaml")
    st.write("**Kategorien** in `config/categories.yaml` anpassen.")
    st.code("kategorien:\n  - Lebensmittel\n  - Restaurant\n  - ...", language="yaml")
st.caption("Tipp: In Safari → Teilen → „Zum Home-Bildschirm“ hinzufügen – dann wirkt es wie eine App.")
