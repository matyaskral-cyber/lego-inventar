from extensions import db
from datetime import datetime


class InventarDilek(db.Model):
    __tablename__ = "inventar_dilky"

    id = db.Column(db.Integer, primary_key=True)
    part_num = db.Column(db.String(50), nullable=False)
    nazev = db.Column(db.String(200), nullable=False)
    barva = db.Column(db.String(100))
    barva_hex = db.Column(db.String(7))
    tvar = db.Column(db.String(200))
    obrazek_url = db.Column(db.String(500))
    pocet_ks = db.Column(db.Integer, default=1)
    poznamka = db.Column(db.Text)
    datum_pridani = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Dilek {self.part_num} {self.nazev}>"


class InventarSet(db.Model):
    __tablename__ = "inventar_sety"

    id = db.Column(db.Integer, primary_key=True)
    set_num = db.Column(db.String(50), nullable=False)
    nazev = db.Column(db.String(200), nullable=False)
    rok = db.Column(db.Integer)
    tema = db.Column(db.String(200))
    obrazek_url = db.Column(db.String(500))
    pocet_dilku_v_setu = db.Column(db.Integer)
    pocet_ks = db.Column(db.Integer, default=1)
    poznamka = db.Column(db.Text)
    datum_pridani = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Set {self.set_num} {self.nazev}>"
