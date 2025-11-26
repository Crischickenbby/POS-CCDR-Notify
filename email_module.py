

# Aprobar y enviar correo (simulado)
@bp_email.route('/email/aprobar/<int:correo_id>')
def aprobar_correo(correo_id):
    # Actualizar estado y simular envío
    flash('Correo aprobado y enviado', 'success')
    return redirect(url_for('email.historial_correos'))
