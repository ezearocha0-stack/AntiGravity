from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from app.models.finance import CuentasPorCobrar
from app.extensions import db
from sqlalchemy.orm import joinedload

receivables_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

@receivables_bp.route('/')
@login_required
def list_accounts():
    estado = request.args.get('estado', 'pendientes')
    
    if estado == 'pagadas':
        cuentas = CuentasPorCobrar.query.options(joinedload(CuentasPorCobrar.factura)).filter(CuentasPorCobrar.estado == 'pagado').order_by(CuentasPorCobrar.created_at.desc()).all()
    elif estado == 'todas':
        cuentas = CuentasPorCobrar.query.options(joinedload(CuentasPorCobrar.factura)).order_by(CuentasPorCobrar.created_at.desc()).all()
    else:
        cuentas = CuentasPorCobrar.query.options(joinedload(CuentasPorCobrar.factura)).filter(CuentasPorCobrar.estado.in_(['pendiente', 'atrasado', 'al_dia', 'parcial'])).filter(CuentasPorCobrar.saldo > 0).order_by(CuentasPorCobrar.created_at.desc()).all()
        
    return render_template('receivables/list.html', cuentas=cuentas, estado=estado)

@receivables_bp.route('/detail/<int:id>')
@login_required
def detail_account(id):
    cuenta = db.session.get(CuentasPorCobrar, id)
    if not cuenta:
        flash('Cuenta por cobrar no encontrada.', 'danger')
        return redirect(url_for('accounts.list_accounts'))
    return render_template('receivables/detail.html', cuenta=cuenta)
