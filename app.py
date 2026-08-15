from flask import Flask, render_template, request, redirect, url_for, flash
from database import conectar, criar_tabelas

app = Flask(__name__)
app.secret_key = 'clinica123'

criar_tabelas()

@app.route('/')
def index():
    conn = conectar()
    agendamentos = conn.execute('''
        SELECT a.id, c.nome, h.data, h.hora, a.observacao, a.cancelado
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN horarios h ON a.horario_id = h.id
        WHERE a.cancelado = 0
        ORDER BY h.data, h.hora
    ''').fetchall()
    conn.close()
    return render_template('index.html', agendamentos=agendamentos)

@app.route('/clientes')
def listar_clientes():
    conn = conectar()
    clientes = conn.execute('SELECT * FROM clientes ORDER BY nome').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/cadastrar', methods=['POST'])
def cadastrar_cliente():
    nome = request.form['nome']
    telefone = request.form['telefone']
    email = request.form['email']
    if not nome or not telefone:
        flash('Nome e telefone são obrigatórios.')
        return redirect(url_for('listar_clientes'))
    conn = conectar()
    conn.execute('INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)',
                 (nome, telefone, email))
    conn.commit()
    conn.close()
    flash('Cliente cadastrado!')
    return redirect(url_for('listar_clientes'))

@app.route('/clientes/excluir/<int:id>')
def excluir_cliente(id):
    conn = conectar()
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Cliente excluído!')
    return redirect(url_for('listar_clientes'))

@app.route('/horarios')
def listar_horarios():
    conn = conectar()
    horarios = conn.execute('SELECT * FROM horarios ORDER BY data, hora').fetchall()
    conn.close()
    return render_template('horarios.html', horarios=horarios)

@app.route('/horarios/cadastrar', methods=['POST'])
def cadastrar_horario():
    data = request.form['data']
    hora = request.form['hora']
    if not data or not hora:
        flash('Data e hora são obrigatórios.')
        return redirect(url_for('listar_horarios'))
    conn = conectar()
    existente = conn.execute('SELECT id FROM horarios WHERE data = ? AND hora = ?',
                             (data, hora)).fetchone()
    if existente:
        flash('Esse horário já existe.')
        conn.close()
        return redirect(url_for('listar_horarios'))
    conn.execute('INSERT INTO horarios (data, hora) VALUES (?, ?)', (data, hora))
    conn.commit()
    conn.close()
    flash('Horário cadastrado!')
    return redirect(url_for('listar_horarios'))

@app.route('/horarios/excluir/<int:id>')
def excluir_horario(id):
    conn = conectar()
    conn.execute('DELETE FROM horarios WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Horário excluído!')
    return redirect(url_for('listar_horarios'))

@app.route('/agendamentos')
def listar_agendamentos():
    conn = conectar()
    clientes = conn.execute('SELECT * FROM clientes ORDER BY nome').fetchall()
    horarios = conn.execute('SELECT * FROM horarios WHERE disponivel = 1 ORDER BY data, hora').fetchall()
    agendamentos = conn.execute('''
        SELECT a.id, c.nome, h.data, h.hora, a.observacao, a.cancelado
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN horarios h ON a.horario_id = h.id
        ORDER BY h.data, h.hora
    ''').fetchall()
    conn.close()
    return render_template('agendamentos.html', clientes=clientes, horarios=horarios, agendamentos=agendamentos)

@app.route('/agendamentos/agendar', methods=['POST'])
def agendar():
    cliente_id = request.form['cliente_id']
    horario_id = request.form['horario_id']
    observacao = request.form.get('observacao', '')
    if not cliente_id or not horario_id:
        flash('Selecione cliente e horário.')
        return redirect(url_for('listar_agendamentos'))
    conn = conectar()
    horario = conn.execute('SELECT * FROM horarios WHERE id = ?', (horario_id,)).fetchone()
    if not horario or not horario['disponivel']:
        flash('Horário não está disponível.')
        conn.close()
        return redirect(url_for('listar_agendamentos'))
    conn.execute('INSERT INTO agendamentos (cliente_id, horario_id, observacao) VALUES (?, ?, ?)',
                 (cliente_id, horario_id, observacao))
    conn.execute('UPDATE horarios SET disponivel = 0 WHERE id = ?', (horario_id,))
    conn.commit()
    conn.close()
    flash('Agendamento realizado!')
    return redirect(url_for('listar_agendamentos'))

@app.route('/agendamentos/cancelar/<int:id>')
def cancelar_agendamento(id):
    conn = conectar()
    agendamento = conn.execute('SELECT * FROM agendamentos WHERE id = ?', (id,)).fetchone()
    if agendamento:
        conn.execute('UPDATE agendamentos SET cancelado = 1 WHERE id = ?', (id,))
        conn.execute('UPDATE horarios SET disponivel = 1 WHERE id = ?', (agendamento['horario_id'],))
        conn.commit()
    conn.close()
    flash('Agendamento cancelado!')
    return redirect(url_for('listar_agendamentos'))

if __name__ == '__main__':
    app.run(debug=True)