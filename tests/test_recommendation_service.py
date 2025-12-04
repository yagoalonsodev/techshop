"""
Tests para Recommendation Service
"""

from tests.test_common import *

def test_recommendations_by_sales():
    init_test_db()  # Asegurar que la BD está inicializada
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=1, user_id=1, product_id=1, quantity=5, price=50.0)
    _insert_sale(conn, order_id=2, user_id=1, product_id=2, quantity=2, price=100.0)
    _insert_sale(conn, order_id=3, user_id=2, product_id=3, quantity=8, price=20.0)
    conn.close()

    recommendations = service.get_top_selling_products(limit=2)
    if not assert_equals(len(recommendations), 2, "Número de recomanacions incorrecte"):
        return False
    top_product, top_total = recommendations[0]
    second_product, second_total = recommendations[1]
    conditions = [
        assert_equals(top_product.id, 3, "El producte més venut ha de ser el 3"),
        assert_equals(top_total, 8, "Unitats venudes esperades per al producte 3"),
        assert_equals(second_product.id, 1, "El segon producte ha de ser el 1"),
        assert_equals(second_total, 5, "Unitats venudes esperades per al producte 1"),
    ]
    return all(conditions)


def test_recommendations_tiebreaker_by_name():
    """
    Quan dos productes tenen les mateixes unitats venudes,
    l'ordre s'ha de decidir pel nom (ORDER BY total_sold DESC, p.name ASC).
    """
    init_test_db()  # Asegurar que la BD está inicializada
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    # Mateixa quantitat venuda (3), però noms diferents
    _insert_sale(conn, order_id=10, user_id=1, product_id=10, quantity=3, price=10.0)  # Product 10
    _insert_sale(conn, order_id=11, user_id=1, product_id=11, quantity=3, price=10.0)  # Product 11
    conn.close()

    recs = service.get_top_selling_products(limit=2)
    if not assert_equals(len(recs), 2, "Han de sortir dos productes en empat"):
        return False
    p1, _ = recs[0]
    p2, _ = recs[1]
    # Per nom alfabètic: "Product 10" ha d'anar abans que "Product 11"
    return assert_true(p1.name < p2.name, "S'hauria d'ordenar per nom en cas d'empat")



def test_recommendations_limit_zero():
    init_test_db()  # Asegurar que la BD está inicializada
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=1, user_id=1, product_id=1, quantity=3, price=10.0)
    conn.close()
    recommendations = service.get_top_selling_products(limit=0)
    return assert_equals(recommendations, [], "Limit zero ha de retornar llista buida")


def test_recommendations_negative_limit():
    """Un límit negatiu s'ha de tractar igual que 0: sense recomanacions."""
    init_test_db()  # Asegurar que la BD está inicializada
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    _insert_sale(conn, order_id=1, user_id=1, product_id=1, quantity=2, price=10.0)
    conn.close()
    recommendations = service.get_top_selling_products(limit=-5)
    return assert_equals(recommendations, [], "Limit negatiu ha de retornar llista buida")



def test_recommendations_no_sales():
    init_test_db()  # Asegurar que la BD está inicializada
    service = RecommendationService('test.db')
    conn = sqlite3.connect('test.db')
    _reset_sales_data(conn)
    conn.close()
    recommendations = service.get_top_selling_products(limit=3)
    return assert_equals(recommendations, [], "Sense vendes no hi ha recomanacions")


def test_recommendations_db_error_returns_empty():
    """Si hi ha un error de BD, el servei de recomanacions ha de retornar llista buida."""
    service = RecommendationService('test.db')
    original_connect = sqlite3.connect

    def failing_connect(*args, **kwargs):
        raise sqlite3.Error("DB down")

    sqlite3.connect = failing_connect
    try:
        recs_all = service.get_top_selling_products(limit=3)
        recs_user = service.get_top_products_for_user(user_id=1, limit=3)
        return assert_equals(recs_all, [], "Amb error de BD s'ha de retornar llista buida (global)") and \
               assert_equals(recs_user, [], "Amb error de BD s'ha de retornar llista buida (per usuari)")
    finally:
        sqlite3.connect = original_connect


# =========================
# TESTOS D'INTEGRACIÓ FLASK
# =========================


