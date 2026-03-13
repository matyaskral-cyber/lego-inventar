import os
import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import InventarSet

sety_bp = Blueprint("sety", __name__, url_prefix="/sety")

REBRICKABLE_BASE = "https://rebrickable.com/api/v3/lego"


def get_api_key():
    return os.environ.get("REBRICKABLE_API_KEY", "")


def fetch_set(set_num):
    key = get_api_key()
    url = f"{REBRICKABLE_BASE}/sets/{set_num}/"
    resp = requests.get(url, params={"key": key}, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return None


@sety_bp.route("/hledat", methods=["GET", "POST"])
def hledat():
    nahled = None
    chyba = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "hledat":
            set_num = request.form.get("set_num", "").strip()
            if not set_num:
                chyba = "Zadej číslo setu."
            else:
                # Rebrickable vyžaduje formát "75192-1" — přidat suffix pokud chybí
                if "-" not in set_num:
                    set_num = set_num + "-1"
                data = fetch_set(set_num)
                if data:
                    nahled = data
                else:
                    chyba = f"Set '{set_num}' nebyl nalezen v Rebrickable."

        elif action == "pridat":
            set_num = request.form.get("set_num", "").strip()
            nazev = request.form.get("nazev", "")
            rok = request.form.get("rok")
            tema = request.form.get("tema", "")
            obrazek_url = request.form.get("obrazek_url", "")
            pocet_dilku_v_setu = request.form.get("pocet_dilku_v_setu")
            pocet_ks = int(request.form.get("pocet_ks", 1))
            poznamka = request.form.get("poznamka", "")

            inv_set = InventarSet(
                set_num=set_num,
                nazev=nazev,
                rok=int(rok) if rok else None,
                tema=tema,
                obrazek_url=obrazek_url,
                pocet_dilku_v_setu=int(pocet_dilku_v_setu) if pocet_dilku_v_setu else None,
                pocet_ks=pocet_ks,
                poznamka=poznamka,
            )
            db.session.add(inv_set)
            db.session.commit()
            flash(f"Set {set_num} přidán do inventáře!", "success")
            return redirect(url_for("sety.prehled"))

    return render_template("sety/hledat.html", nahled=nahled, chyba=chyba)


@sety_bp.route("/", methods=["GET"])
def prehled():
    filtr_tema = request.args.get("tema", "")

    query = InventarSet.query
    if filtr_tema:
        query = query.filter(InventarSet.tema.ilike(f"%{filtr_tema}%"))

    sety = query.order_by(InventarSet.datum_pridani.desc()).all()
    vsechna_temata = db.session.query(InventarSet.tema).distinct().filter(InventarSet.tema != None).all()

    return render_template(
        "sety/prehled.html",
        sety=sety,
        filtr_tema=filtr_tema,
        vsechna_temata=[t[0] for t in vsechna_temata if t[0]],
    )


@sety_bp.route("/<int:id>/upravit-pocet", methods=["POST"])
def upravit_pocet(id):
    inv_set = InventarSet.query.get_or_404(id)
    akce = request.form.get("akce")
    if akce == "plus":
        inv_set.pocet_ks += 1
    elif akce == "minus" and inv_set.pocet_ks > 1:
        inv_set.pocet_ks -= 1
    elif akce == "nastavit":
        novy = int(request.form.get("pocet", inv_set.pocet_ks))
        inv_set.pocet_ks = max(1, novy)
    db.session.commit()
    return redirect(url_for("sety.prehled"))


@sety_bp.route("/<int:id>/smazat", methods=["POST"])
def smazat(id):
    inv_set = InventarSet.query.get_or_404(id)
    db.session.delete(inv_set)
    db.session.commit()
    flash(f"Set {inv_set.set_num} smazán.", "info")
    return redirect(url_for("sety.prehled"))
