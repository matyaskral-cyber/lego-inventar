import os
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import InventarDilek

dilky_bp = Blueprint("dilky", __name__, url_prefix="/dilky")

REBRICKABLE_BASE = "https://rebrickable.com/api/v3/lego"


def get_api_key():
    return os.environ.get("REBRICKABLE_API_KEY", "")


def fetch_part(part_num):
    key = get_api_key()
    url = f"{REBRICKABLE_BASE}/parts/{part_num}/"
    resp = requests.get(url, params={"key": key}, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return None


def fetch_part_colors(part_num):
    """Vrátí seznam barev pro daný dílek."""
    key = get_api_key()
    url = f"{REBRICKABLE_BASE}/parts/{part_num}/colors/"
    resp = requests.get(url, params={"key": key, "page_size": 100}, timeout=10)
    if resp.status_code == 200:
        return resp.json().get("results", [])
    return []


@dilky_bp.route("/hledat", methods=["GET", "POST"])
def hledat():
    nahled = None
    barvy = []
    chyba = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "hledat":
            part_num = request.form.get("part_num", "").strip()
            if not part_num:
                chyba = "Zadej číslo dílku."
            else:
                data = fetch_part(part_num)
                if data:
                    nahled = data
                    barvy = fetch_part_colors(part_num)
                else:
                    chyba = f"Dílek '{part_num}' nebyl nalezen v Rebrickable."

        elif action == "pridat":
            part_num = request.form.get("part_num", "").strip()
            nazev = request.form.get("nazev", "")
            barva = request.form.get("barva", "")
            barva_hex = request.form.get("barva_hex", "")
            tvar = request.form.get("tvar", "")
            obrazek_url = request.form.get("obrazek_url", "")
            pocet_ks = int(request.form.get("pocet_ks", 1))
            poznamka = request.form.get("poznamka", "")

            dilek = InventarDilek(
                part_num=part_num,
                nazev=nazev,
                barva=barva,
                barva_hex=barva_hex,
                tvar=tvar,
                obrazek_url=obrazek_url,
                pocet_ks=pocet_ks,
                poznamka=poznamka,
            )
            db.session.add(dilek)
            db.session.commit()
            flash(f"Dílek {part_num} přidán do inventáře!", "success")
            return redirect(url_for("dilky.prehled"))

    return render_template("dilky/hledat.html", nahled=nahled, barvy=barvy, chyba=chyba)


@dilky_bp.route("/", methods=["GET"])
def prehled():
    filtr_barva = request.args.get("barva", "")
    filtr_tvar = request.args.get("tvar", "")

    query = InventarDilek.query
    if filtr_barva:
        query = query.filter(InventarDilek.barva.ilike(f"%{filtr_barva}%"))
    if filtr_tvar:
        query = query.filter(InventarDilek.tvar.ilike(f"%{filtr_tvar}%"))

    dilky = query.order_by(InventarDilek.datum_pridani.desc()).all()

    vsechny_barvy = db.session.query(InventarDilek.barva).distinct().filter(InventarDilek.barva != None).all()
    vsechny_tvary = db.session.query(InventarDilek.tvar).distinct().filter(InventarDilek.tvar != None).all()

    return render_template(
        "dilky/prehled.html",
        dilky=dilky,
        filtr_barva=filtr_barva,
        filtr_tvar=filtr_tvar,
        vsechny_barvy=[b[0] for b in vsechny_barvy if b[0]],
        vsechny_tvary=[t[0] for t in vsechny_tvary if t[0]],
    )


@dilky_bp.route("/<int:id>/upravit-pocet", methods=["POST"])
def upravit_pocet(id):
    dilek = InventarDilek.query.get_or_404(id)
    akce = request.form.get("akce")
    if akce == "plus":
        dilek.pocet_ks += 1
    elif akce == "minus" and dilek.pocet_ks > 1:
        dilek.pocet_ks -= 1
    elif akce == "nastavit":
        novy = int(request.form.get("pocet", dilek.pocet_ks))
        dilek.pocet_ks = max(1, novy)
    db.session.commit()
    return redirect(url_for("dilky.prehled") + request.args.get("zpet", ""))


@dilky_bp.route("/<int:id>/smazat", methods=["POST"])
def smazat(id):
    dilek = InventarDilek.query.get_or_404(id)
    db.session.delete(dilek)
    db.session.commit()
    flash(f"Dílek {dilek.part_num} smazán.", "info")
    return redirect(url_for("dilky.prehled"))
