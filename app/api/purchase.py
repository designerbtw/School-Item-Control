from flask import request, jsonify
from app import db, logger
from app.models import Purchase
from app.utils.json_is_valid import json_is_valid
from . import module

@module.route('/create_purchase', methods=['POST'])
@json_is_valid({"name": str, "quantity": int, "price": int, "supplier": str})
def create_purchase():
    """
    Создает новую закупку.

    JSON тело запроса:
        - name (str): Название товара в закупку.
        - supplier (str): Название поставщика.
        - price (int): Плановая цена товара.
        - quantity (int): Количество товара в покупке.

    :return: JSON ответ:
        - status (str): 'success', если закупка успешно создана.
        - HTTP статус код 201.
    """
    try:
        name = request.json['name']
        supplier = request.json['supplier']
        price = request.json['price']
        quantity = request.json['quantity']

        # Проверка входных значений
        if price <= 0:
            return jsonify({"status": "error", "message": "Цена должна быть больше нуля"}), 400
        if quantity < 0:
            return jsonify({"status": "error", "message": "Количество не может быть отрицательным"}), 400

        # Создание новой закупки
        purchase = Purchase(name=name, quantity=quantity, price=price, supplier=supplier)

        db.session.add(purchase)
        db.session.commit()

        return jsonify({"status": "success", "id": purchase.id}), 201
    except Exception as e:
        logger.error(f"Ошибка при создании покупки: {e}. Данные запроса: {request.json}")
        return jsonify({"status": "error", "message": "Ошибка при создании покупки"}), 500


@module.route('/delete_purchase', methods=['DELETE'])
@json_is_valid({"id": int})
def delete_purchase():
    """
    Удаляет закупку.

    JSON тело запроса:
        - id (int): ID закупку.

    :return: JSON ответ:
        - status (str): 'success', если закупка успешно удалена.
        - HTTP статус код 200.
    """
    try:
        id = request.json['id']

        purchase = Purchase.query.get(id)

        if not purchase:
            return jsonify({"status": "error", "message": f"Покупка с ID {id} не найдена"}), 404

        db.session.delete(purchase)
        db.session.commit()

        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Ошибка при удалении покупки: {e}. Данные запроса: {request.json}")
        return jsonify({"status": "error", "message": "Ошибка при удалении покупки"}), 500


@module.route('/purchases', methods=['GET'])
def get_purchases():
    """
    Получает все текущие закупки.

    :return: JSON ответ:
        - purchases (list): Список всех закупок.
        - HTTP статус код 200.
    """
    try:
        purchases = Purchase.query.all()
        purchases_list = [
            {
                "id": purchase.id,
                "name": purchase.name,
                "quantity": purchase.quantity,
                "supplier": purchase.supplier,
                "price": purchase.price,
                "created_at": purchase.created_at.isoformat()
            }
            for purchase in purchases
        ]

        return jsonify({"status": "success", "purchases": purchases_list}), 200
    except Exception as e:
        logger.error(f"Ошибка при получении покупок: {e}")
        return jsonify({"status": "error", "message": "Ошибка при получении покупок"}), 500
