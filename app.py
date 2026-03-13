import os
from flask import Flask, render_template
from dotenv import load_dotenv
from extensions import db

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "lego-dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lego_inventar.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from routes.dilky import dilky_bp
    from routes.sety import sety_bp

    app.register_blueprint(dilky_bp)
    app.register_blueprint(sety_bp)

    @app.route("/")
    def dashboard():
        from models import InventarDilek, InventarSet
        pocet_dilku = InventarDilek.query.count()
        pocet_setu = InventarSet.query.count()
        celkem_ks_dilky = db.session.query(db.func.sum(InventarDilek.pocet_ks)).scalar() or 0
        celkem_ks_sety = db.session.query(db.func.sum(InventarSet.pocet_ks)).scalar() or 0
        posledni_dilky = InventarDilek.query.order_by(InventarDilek.datum_pridani.desc()).limit(5).all()
        posledni_sety = InventarSet.query.order_by(InventarSet.datum_pridani.desc()).limit(5).all()
        return render_template(
            "dashboard.html",
            pocet_dilku=pocet_dilku,
            pocet_setu=pocet_setu,
            celkem_ks_dilky=celkem_ks_dilky,
            celkem_ks_sety=celkem_ks_sety,
            posledni_dilky=posledni_dilky,
            posledni_sety=posledni_sety,
        )

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5050)
