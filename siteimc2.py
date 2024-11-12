from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

import MySQLdb.cursors
import re



app=Flask(__name__)


app.secret_key = 'passpi2univesp'

app.config['MYSQL_HOST'] = '145.223.31.145'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'UnivPi0811!'
app.config['MYSQL_DB'] = 'piunivespi2'

mysql = MySQL(app)

@app.route("/")
def index():
    session['loggedin'] = False
    return render_template("index.html")

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        username = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE email = % s AND senha = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['codusuario']
            session['username'] = account['nome']
            session['email'] = account['email']
            msg = 'Logado com sucesso!'
            bemvindo = 'Bem-vindo(a), ' + session['username'] + '!'
            cursorregistros = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = """
                select 
	                date_format(registros.dtregistro,'%%d/%%m/%%Y') as dataregistro, 
	                registros.alturam, 
	                registros.pesokg, 
	                format(((pesokg) / ((alturam)*(alturam))),1) as imc, 
	                (case
		                when (pesokg)/((alturam)*(alturam)) < 18.5 then 'baixo peso' 
		                when (pesokg)/((alturam)*(alturam)) >=18.5 and (pesokg)/((alturam)*(alturam)) < 25 then 'normal' 
		                when (pesokg)/((alturam)*(alturam)) >=25 and (pesokg)/((alturam)*(alturam)) < 30 then 'sobrepeso' 
		                when (pesokg)/((alturam)*(alturam)) >=30 and (pesokg)/((alturam)*(alturam)) < 35 then 'obesidade classe I' 
		                when (pesokg)/((alturam)*(alturam)) >=35 and (pesokg)/((alturam)*(alturam)) < 40 then 'obesidade classe II' 
		                when (pesokg)/((alturam)*(alturam)) >=40 then 'obesidade classe III' 
		                else '0'
	                end) as status
                from 
	                piunivespimc.registros 
                inner join piunivespimc.usuarios on registros.regcodusuario = usuarios.codusuario
                where 
	                registros.regcodusuario = % s 
                order by 
	            dtregistro desc
            """
            cursorregistros.execute(sql, (session['id'],))
            resultados = cursorregistros.fetchall()
            #for rows in resultados:
            #    print(rows)
            return render_template('home.html', bemvindo = bemvindo , resultados = resultados)
        else:
            msg = 'Email ou senha incorretos'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/cadastrar", methods =['GET', 'POST'])
def cadastrar():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'passwordconf' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        passwordconf = request.form['passwordconf']
        email = request.form['email']
        if password == passwordconf :
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM usuarios WHERE email = % s', (email, ))
            account = cursor.fetchone()
            if account:
                msg = 'Esse email já está cadastrado'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Email inválido'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Nome deve conter apenas letras e números !'
            elif not username or not password or not email:
                msg = 'Por favor, preencha seus dados!'
            else:
                cursor.execute('INSERT INTO usuarios VALUES (NULL, % s, % s, % s)', (email, password, username, ))
                mysql.connection.commit()
                msg = 'Usuário cadastrado com sucesso!'
                return render_template("index.html")
        else :
            msg = 'As senhas não estão iguais'
    elif request.method == 'POST':
        msg = 'Por favor, preencha os dados'
    return render_template('cadastrar.html', msg = msg)

@app.route("/inserir", methods =['GET', 'POST'])
def inserir():
    if session['loggedin'] == True:
        bemvindo = ''
        msg = ''
        if request.method == 'POST' and 'altura' in request.form and 'peso' in request.form and 'dt' in request.form:
            altura = request.form['altura']
            peso = request.form['peso']
            dt = request.form['dt']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO registros VALUES (NULL, % s, % s, % s, % s)', (peso, altura, dt, session['id'],))
            mysql.connection.commit()
            msg = 'Dados inseridos com sucesso!'
            bemvindo = 'Bem-vindo(a), ' + session['username'] + '!'
            cursorregistros = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            sql = """
                            select 
            	                date_format(registros.dtregistro,'%%d/%%m/%%Y') as dataregistro, 
            	                registros.alturam, 
            	                registros.pesokg, 
            	                format(((pesokg) / ((alturam)*(alturam))),1) as imc, 
            	                (case
            		                when (pesokg)/((alturam)*(alturam)) < 18.5 then 'baixo peso' 
            		                when (pesokg)/((alturam)*(alturam)) >=18.5 and (pesokg)/((alturam)*(alturam)) < 25 then 'normal' 
            		                when (pesokg)/((alturam)*(alturam)) >=25 and (pesokg)/((alturam)*(alturam)) < 30 then 'sobrepeso' 
            		                when (pesokg)/((alturam)*(alturam)) >=30 and (pesokg)/((alturam)*(alturam)) < 35 then 'obesidade classe I' 
            		                when (pesokg)/((alturam)*(alturam)) >=35 and (pesokg)/((alturam)*(alturam)) < 40 then 'obesidade classe II' 
            		                when (pesokg)/((alturam)*(alturam)) >=40 then 'obesidade classe III' 
            		                else '0'
            	                end) as status
                            from 
            	                piunivespimc.registros 
                            inner join piunivespimc.usuarios on registros.regcodusuario = usuarios.codusuario
                            where 
            	                registros.regcodusuario = % s 
                            order by 
            	            dtregistro desc
                        """
            cursorregistros.execute(sql, (session['id'],))
            resultados = cursorregistros.fetchall()

            return render_template('home.html', bemvindo=bemvindo , resultados=resultados)
        return render_template('inserir.html', msg = msg)

    else:
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
