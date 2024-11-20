from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from .config import supabase

app_bp = Blueprint("app", __name__)

from datetime import datetime

def get_dashboard_data():
    earnings_response = supabase.table('earnings').select("*").execute()
    expenses_response = supabase.table('expenses').select("*").execute()

    earnings = earnings_response.data
    expenses = expenses_response.data

    # Calcular total de earnings e expenses
    earnings_total = sum([float(item['amount']) for item in earnings])
    expenses_total = sum([float(item['amount']) for item in expenses])
    balance = earnings_total - expenses_total

    # Categorizar despesas
    category_totals = {}
    for expense in expenses:
        category = expense['category']
        amount = float(expense['amount'])
        category_totals[category] = category_totals.get(category, 0) + amount

    expense_categories = []
    for category, total in category_totals.items():
        percentage = (total / expenses_total * 100) if expenses_total > 0 else 0
        expense_categories.append({
            "name": category,
            "percentage": round(percentage, 2),
            "color": "#{:06x}".format(hash(category) & 0xFFFFFF)  # Gerar cor
        })

    # Unir e ordenar transações
    transactions = [
        {**transaction, "tipo": "entrada"} for transaction in earnings
    ] + [
        {**transaction, "tipo": "saida"} for transaction in expenses
    ]
    # Ordena as transações pela data, da mais recente para a mais antiga
    transactions.sort(key=lambda x: datetime.fromisoformat(x['date']), reverse=True)

    return {
        "balance": format(balance, ",.2f"),
        "incomes": format(earnings_total, ",.2f"),
        "expenses": format(expenses_total, ",.2f"),
        "expense_categories": expense_categories,
        "transactions": transactions
    }


@app_bp.route("/")
def home():
    dashboard_data = get_dashboard_data()
    return render_template("index.html", **dashboard_data)

@app_bp.route('/income', methods=['POST'])
def add_income():
    amount = float(request.form.get('amount'))
    description = request.form.get('description')
    payment_method = request.form.get('payment_method')
    
    supabase.table('earnings').insert({
        'amount': amount,
        'category': description
    }).execute()
    
    flash("Income added successfully!", "success")
    return redirect(url_for('app.home'))

@app_bp.route('/expense', methods=['POST'])
def add_expense():
    amount = float(request.form.get('amount'))
    description = request.form.get('description')
    payment_method = request.form.get('payment_method')
    category = request.form.get('category')
    
    supabase.table('expenses').insert({
        'amount': amount,
        'category': category
    }).execute()
    
    flash("Expense added successfully!", "success")
    return redirect(url_for('app.home'))
